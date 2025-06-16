from datetime import datetime
from .mongo import update_global_metrics
import time
from bson import ObjectId
from rest_framework import serializers
from .models import Document, Collection
from .mongo import get_documents_collection
from .utils import compute_global_tfidf_table


class TFIDFUploadSerializer(serializers.Serializer):
	files = serializers.ListField(
		child=serializers.FileField(),
		allow_empty=False,
		write_only=True
	)

	def validate(self, data):
		decoded_texts = []
		for f in data['files']:
			try:
				content = f.read().decode('utf-8').strip()
				decoded_texts.append(content)
				f.seek(0)
			except UnicodeDecodeError:
				raise serializers.ValidationError(f"File '{f.name}' is not UTF-8 encoded.")
		data['decoded_texts'] = decoded_texts
		return data

	def create(self, validated_data):
		user = self.context['request'].user
		files = validated_data['files']
		texts = validated_data['decoded_texts']

		start_time = time.time()
		# Считаем TF-IDF, но не сохраняем в БД
		tfidf_results, word_counts = compute_global_tfidf_table(texts)
		now = datetime.utcnow().isoformat()

		documents_collection = get_documents_collection()

		# В Mongo сохраняем только контент без статистики
		documents = [{
			"file_name": f.name,
			"file_size": f.size,
			"word_count": wc,
			"content": text,  # только содержимое
			"uploaded_at": now
		} for f, text, wc in zip(files, texts, word_counts)]

		result = documents_collection.insert_many(documents)
		inserted_ids = result.inserted_ids

		# В PostgreSQL сохраняем метаданные (тоже без tfidf_data)
		for f, wc, mongo_id in zip(files, word_counts, inserted_ids):
			Document.objects.create(
				user=user,
				name=f.name,
				size=f.size,
				word_count=wc,
				mongo_id=str(mongo_id)
			)

		processing_time = round(time.time() - start_time, 3)
		update_global_metrics(processing_time, len(files))

		# Выводим топ-50 слов по TF-IDF из расчёта (не из БД)
		top_words = []
		if tfidf_results:
			for i, item in enumerate(tfidf_results[0]):
				word = item["word"]
				idf = item["idf"]
				avg_tf = round(
					sum(doc[i]["tf"] for doc in tfidf_results) / len(tfidf_results), 6
				)
				top_words.append({"word": word, "idf": idf, "tf": avg_tf})

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
	tf = serializers.FloatField(source='total_tf')
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
