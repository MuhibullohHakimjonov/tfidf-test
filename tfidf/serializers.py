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
		oversized = [f.name for f in files if f.size > MAX_FILE_SIZE]
		if oversized:
			raise serializers.ValidationError(f"Files too large: {', '.join(oversized)}")

		for f in files:
			try:
				f.read().decode('utf-8').strip()
				f.seek(0)
			except UnicodeDecodeError:
				raise serializers.ValidationError("Only UTF-8 encoded text files are allowed.")

		return files

	def create(self, validated_data):
		user = self.context['request'].user
		files = validated_data['files']
		texts = [f.read().decode('utf-8').strip() for f in files]

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

		for f, wc, mongo_id in zip(files, word_counts, inserted_ids):
			Document.objects.create(
				user=user,
				name=f.name,
				size=f.size,
				word_count=wc,
				mongo_id=str(mongo_id)
			)

		top_words = []
		if tfidf_results:
			for i, item in enumerate(tfidf_results[0][:50]):
				word = item["word"]
				idf = item["idf"]
				avg_tf = sum(doc[i]["tf"] for doc in tfidf_results if i < len(doc)) / len(tfidf_results)
				top_words.append({
					"word": word,
					"idf": round(idf, 6),
					"tf": round(avg_tf, 6)
				})

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


class CollectionStatisticsSerializer(serializers.Serializer):
	collection_id = serializers.IntegerField()
	documents_count = serializers.IntegerField()
	top_words = serializers.ListField(
		child=serializers.DictField(
			child=serializers.FloatField()  # для tf/idf, строка для слова
		)
	)

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
