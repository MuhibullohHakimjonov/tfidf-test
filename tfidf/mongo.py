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


def get_mongo_collections():
	db = get_mongo_db()
	return {
		"db": db,
		"documents_collection": db["documents"],
	}
