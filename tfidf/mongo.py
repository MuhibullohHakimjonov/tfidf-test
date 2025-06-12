from datetime import datetime

from pymongo import MongoClient
from django.conf import settings


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
				"total_files_uploaded": total_files,  # ← обновляем файлы
				"total_processing_time": total_processing,
				"min_time_processed": min_time,
				"max_time_processed": max_time,
				"sum_time_processed": sum_time,
				"latest_file_processed_timestamp": timestamp
			}}
		)
