from pymongo import MongoClient
from django.conf import settings


def get_mongo_db():
	try:
		client = MongoClient(settings.MONGO_URI)
		return client[settings.MONGO_DB_NAME]
	except Exception as e:
		raise Exception(f"Failed to connect to MongoDB: {str(e)}")


def get_files_collection():
	return get_mongo_db()['files']




def get_mongo_collections():
	try:
		client = MongoClient(settings.MONGO_URI)
		db = client[settings.MONGO_DB_NAME]
		return {
			"client": client,
			"db": db,
			"files_collection": db["files"],
		}
	except Exception as e:
		raise ConnectionError(f"Failed to connect to MongoDB: {e}")
