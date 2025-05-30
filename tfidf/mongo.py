from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]


def get_mongo_db():
	return db


def get_files_collection():
	return db['files']


def get_mongo_collections():
	return {
		"client": client,
		"db": db,
		"files_collection": db["files"],
	}
