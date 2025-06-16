from datetime import datetime

from bson import ObjectId
from pymongo import MongoClient
from django.conf import settings

from .utils import compute_global_tfidf_table


def get_mongo_db():
	username = settings.MONGO['USERNAME']
	password = settings.MONGO['PASSWORD']
	host = settings.MONGO['HOST']
	port = settings.MONGO['PORT']
	db_name = settings.MONGO['DB_NAME']

	uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource=admin"
	client = MongoClient(uri)
	return client[db_name]


def get_documents_collection():
	return get_mongo_db()["documents"]


def get_metrics_collection():
	return get_mongo_db()["metrics_collection"]


def get_mongo_collections():
	db = get_mongo_db()
	return {
		"db": db,
		"documents_collection": db["documents"],
		"metrics_collection": db["metrics_collection"]
	}


def update_global_metrics(processing_time: float, files_count: int):
	metrics_collection = get_metrics_collection()
	timestamp = round(datetime.now().timestamp(), 3)
	metrics = metrics_collection.find_one({"_id": "global_metrics"})

	if not metrics:
		new_metrics = {
			"_id": "global_metrics",
			"total_files_uploaded": files_count,
			"total_batches_uploaded": 1,
			"total_processing_time": round(processing_time, 3),
			"min_time_processed": round(processing_time, 3),
			"max_time_processed": round(processing_time, 3),
			"sum_time_processed": round(processing_time, 3),
			"latest_file_processed_timestamp": timestamp,
		}
		metrics_collection.insert_one(new_metrics)
	else:
		total_batches = metrics.get("total_batches_uploaded", 0) + 1
		total_files = metrics.get("total_files_uploaded", 0) + files_count
		total_processing = round(metrics["total_processing_time"] + processing_time, 3)
		min_time = round(min(metrics["min_time_processed"], processing_time), 3)
		max_time = round(max(metrics["max_time_processed"], processing_time), 3)
		sum_time = round(metrics["sum_time_processed"] + processing_time, 3)

		metrics_collection.update_one(
			{"_id": "global_metrics"},
			{"$set": {
				"total_batches_uploaded": total_batches,
				"total_files_uploaded": total_files,
				"total_processing_time": total_processing,
				"min_time_processed": min_time,
				"max_time_processed": max_time,
				"sum_time_processed": sum_time,
				"latest_file_processed_timestamp": timestamp
			}}
		)


def update_collection_statistics_in_mongo(collection):
	mongo_ids = [doc.mongo_id for doc in collection.documents.all()]
	documents = list(get_documents_collection().find({
		"_id": {"$in": [ObjectId(mongo_id) for mongo_id in mongo_ids]}
	}))

	if not documents:
		raise ValueError("No documents found in MongoDB for this collection.")

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

	top_words = sorted(tfidf_combined, key=lambda x: x["idf"], reverse=True)[:50]

	collection_stats_collection = get_mongo_db()["collection_statistics"]
	collection_stats_collection.update_one(
		{"collection_id": collection.id},
		{
			"$set": {
				"collection_id": collection.id,
				"documents_count": len(documents),
				"top_words": top_words,
				"computed_at": datetime.utcnow().isoformat()
			}
		},
		upsert=True
	)
