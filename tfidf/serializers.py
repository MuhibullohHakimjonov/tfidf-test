import math
from collections import defaultdict, Counter
from datetime import datetime
from multiprocessing import Pool, cpu_count

from bson import ObjectId
from rest_framework import serializers
from .models import Document, Collection
from .mongo import get_documents_collection
from .utils import process_file_content, process_text

from gensim.corpora import Dictionary
from gensim.models import TfidfModel


class TFIDFUploadSerializer(serializers.Serializer):
	files = serializers.ListField(
		child=serializers.FileField(),
		allow_empty=False,
		write_only=True
	)

	def validate_files(self, files):
		# Ограничение отключено — nginx проверяет размер
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

		raw_texts = [f.read() for f in files]

		# multiprocessing токенизация
		with Pool(processes=min(cpu_count(), len(raw_texts))) as pool:
			tokenized_docs = pool.map(process_file_content, raw_texts)

		dictionary = Dictionary(tokenized_docs)
		corpus = [dictionary.doc2bow(text) for text in tokenized_docs]
		tfidf_model = TfidfModel(corpus)
		tfidf_corpus = tfidf_model[corpus]

		idfs = {}
		N = len(corpus)
		for word_id, freq in dictionary.dfs.items():
			idfs[dictionary[word_id]] = math.log(N / freq)

		# top 50 по IDF
		top_words = sorted(idfs.items(), key=lambda x: x[1], reverse=True)[:50]
		top_words_list = [word for word, _ in top_words]

		tfidf_results = []
		word_counts = []

		for doc_tokens, doc_tfidf in zip(tokenized_docs, tfidf_corpus):
			word_count = len(doc_tokens)
			word_counts.append(word_count)

			tf_counter = Counter(doc_tokens)
			doc_result = []
			for word in top_words_list:
				tf = tf_counter[word] / word_count if word_count else 0
				idf = idfs.get(word, 0)
				doc_result.append({
					"word": word,
					"tf": round(tf, 6),
					"idf": round(idf, 6)
				})
			tfidf_results.append(doc_result)

		documents_collection = get_documents_collection()
		now = datetime.utcnow().isoformat()
		documents = []

		for f, tokens, tfidf, wc in zip(files, tokenized_docs, tfidf_results, word_counts):
			documents.append({
				"file_name": f.name,
				"file_size": f.size,
				"word_count": wc,
				"content": ' '.join(tokens),
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

		# возвращаем top_words с усреднённым tf
		top_words_return = []
		if tfidf_results:
			for i, item in enumerate(tfidf_results[0][:50]):
				word = item["word"]
				idf = item["idf"]
				avg_tf = sum(doc[i]["tf"] for doc in tfidf_results if i < len(doc)) / len(tfidf_results)
				top_words_return.append({
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
			"top_words": top_words_return
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
	def from_collection(cls, collection):
		mongo_ids = [doc.mongo_id for doc in collection.documents.all()]
		documents = list(get_documents_collection().find({
			"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}
		}))

		if not documents:
			raise serializers.ValidationError("No documents found in MongoDB")

		texts = [doc.get("content", "") for doc in documents]

		# multiprocessing токенизация
		with Pool(processes=min(cpu_count(), len(texts))) as pool:
			tokenized_docs = pool.map(process_text, texts)

		dictionary = Dictionary(tokenized_docs)
		corpus = [dictionary.doc2bow(text) for text in tokenized_docs]
		tfidf_model = TfidfModel(corpus)
		tfidf_corpus = tfidf_model[corpus]

		idfs = {}
		N = len(corpus)
		for word_id, freq in dictionary.dfs.items():
			idfs[dictionary[word_id]] = math.log(N / freq)

		tf_aggregated = Counter()
		for doc_tokens in tokenized_docs:
			tf_counter = Counter(doc_tokens)
			total_words = len(doc_tokens)
			for word, count in tf_counter.items():
				tf = count / total_words if total_words else 0
				tf_aggregated[word] += tf

		# взять top 50 по IDF
		top_words = sorted(idfs.items(), key=lambda x: x[1], reverse=True)[:50]
		top_words_list = [word for word, _ in top_words]

		top_words_stats = []
		for word in top_words_list:
			idf = idfs.get(word, 0)
			total_tf = tf_aggregated.get(word, 0)
			top_words_stats.append({
				"word": word,
				"total_tf": round(total_tf, 6),
				"idf": round(idf, 6)
			})

		return cls({
			"collection_id": collection.id,
			"documents_count": len(documents),
			"top_words": top_words_stats
		})
