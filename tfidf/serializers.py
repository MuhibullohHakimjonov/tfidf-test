from collections import defaultdict
from datetime import datetime

from bson import ObjectId
from rest_framework import serializers
from .models import Document, Collection
from .mongo import get_documents_collection
from .utils import compute_global_tfidf_table

MAX_FILE_SIZE = 6 * 1024 * 1024


class TFIDFUploadSerializer(serializers.Serializer):
	files = serializers.ListField(
		child=serializers.FileField(),
		allow_empty=False,
		write_only=True
	)

	def validate_files(self, files):
		"""
		Validate each file:
		  - Ensure none exceed the MAX_FILE_SIZE.
		  - Ensure file content can be decoded as UTF-8.
		  - Cache the file content in an attribute (_cached_content) to avoid re-reading.
		"""
		oversized = [f.name for f in files if f.size > MAX_FILE_SIZE]
		if oversized:
			raise serializers.ValidationError(f"Files too large: {', '.join(oversized)}")

		for f in files:
			content = f.read()  # read file content once
			try:
				content.decode('utf-8')
			except UnicodeDecodeError:
				raise serializers.ValidationError("Only UTF-8 encoded text files are allowed.")
			# Cache file content on the file object so we don't need to re-read it
			f._cached_content = content
			f.seek(0)  # reset file pointer
		return files

	def create(self, validated_data):
		user = self.context['request'].user
		files = validated_data['files']
		texts = []

		# Use cached content from validate_files()
		for f in files:
			content = f._cached_content.decode('utf-8').strip()
			texts.append(content)
			f.seek(0)  # reset pointer if needed later

		tfidf_results, word_counts = compute_global_tfidf_table(texts)
		documents_collection = get_documents_collection()
		now = datetime.utcnow().isoformat()

		documents = []
		for f, text, tfidf, wc in zip(files, texts, tfidf_results, word_counts):
			documents.append({
				"file_name": f.name,
				"file_size": f.size,
				"word_count": wc,
				"content": text,
				"tfidf_data": tfidf,
				"uploaded_at": now
			})

		result = documents_collection.insert_many(documents)
		inserted_ids = result.inserted_ids

		# Write file meta to PostgreSQL
		for f, wc, mongo_id in zip(files, word_counts, inserted_ids):
			Document.objects.create(
				user=user,
				name=f.name,
				size=f.size,
				word_count=wc,
				mongo_id=str(mongo_id)
			)

		# Compute average TF and gather top words across all documents
		# Use cumulative sum and count for efficiency
		tf_idf_map = defaultdict(lambda: {'idf': 0, 'tf_sum': 0, 'count': 0})
		for doc_result in tfidf_results:
			for word_info in doc_result:
				word = word_info["word"]
				tf_idf_map[word]['idf'] = word_info["idf"]
				tf_idf_map[word]['tf_sum'] += word_info["tf"]
				tf_idf_map[word]['count'] += 1

		# Compute top words sorted by idf descending
		sorted_words = sorted(tf_idf_map.items(), key=lambda x: x[1]['idf'], reverse=True)[:50]
		top_words = [
			{
				"word": word,
				"idf": round(info['idf'], 6),
				"tf": round(info['tf_sum'] / info['count'], 6)
			}
			for word, info in sorted_words
		]

		return {
			"files": [
				{
					"file_id": str(fid),
					"file_name": f.name,
					"file_size": f.size,
					"word_count": wc
				}
				for f, wc, fid in zip(files, word_counts, inserted_ids)
			],
			"top_words": top_words
		}


class TfidfEntrySerializer(serializers.Serializer):
	word = serializers.CharField()
	tf = serializers.FloatField()
	idf = serializers.FloatField()


class CollectionSampleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Collection
		fields = ['id', 'name']


class DocumentStatisticsSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	name = serializers.CharField()
	word_count = serializers.IntegerField()
	file_size = serializers.IntegerField(source="size")
	uploaded_at = serializers.DateTimeField(source="created_at")
	collections = CollectionSampleSerializer(many=True)
	tfidf_data = TfidfEntrySerializer(many=True)

	def to_representation(self, instance):
		mongo_doc = instance
		document = self.context["document"]

		base = super().to_representation({
			"id": document.id,
			"name": document.name,
			"size": document.size,
			"word_count": document.word_count,
			"created_at": document.created_at,
			"collections": document.collections.all(),
			"tfidf_data": mongo_doc.get("tfidf_data", [])
		})

		return base


class DocumentSerializer(serializers.ModelSerializer):
	collections = CollectionSampleSerializer(read_only=True, many=True)

	class Meta:
		model = Document
		fields = ['id', 'name', 'size', 'word_count', 'created_at', 'mongo_id', 'collections']


class CollectionSerializer(serializers.ModelSerializer):
	documents = DocumentSerializer(many=True)

	class Meta:
		model = Collection
		fields = ['id', 'name', 'documents']


class CollectionCreateSerializer(serializers.Serializer):
	name = serializers.CharField(max_length=255)


class WordStatsSerializer(serializers.Serializer):
	word = serializers.CharField()
	total_tf = serializers.FloatField()
	idf = serializers.FloatField()


class CollectionStatisticsSerializer(serializers.Serializer):
	collection_id = serializers.IntegerField()
	documents_count = serializers.IntegerField()
	top_words = WordStatsSerializer(many=True)

	@classmethod
	def from_collection(cls, collection: Collection):
		mongo_ids = [doc.mongo_id for doc in collection.documents.all()]
		documents = list(get_documents_collection().find({
			"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}
		}))

		if not documents:
			raise serializers.ValidationError("No documents found in MongoDB")

		texts = [doc.get("content", "") for doc in documents]
		tfidf_results, _ = compute_global_tfidf_table(texts)

		tf_aggregated = {}
		for doc in tfidf_results:
			for entry in doc:
				word = entry["word"]
				tf_aggregated[word] = tf_aggregated.get(word, 0) + entry["tf"]

		idf_lookup = {entry["word"]: entry["idf"] for entry in tfidf_results[0]}

		tfidf_combined = [
			{
				"word": word,
				"total_tf": round(tf, 6),
				"idf": round(idf_lookup[word], 6)
			}
			for word, tf in tf_aggregated.items()
		]

		tfidf_sorted = sorted(tfidf_combined, key=lambda x: x["idf"], reverse=True)[:50]

		return cls({
			"collection_id": collection.id,
			"documents_count": len(documents),
			"top_words": tfidf_sorted
		})
