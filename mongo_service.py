from pymongo import MongoClient
import json
from bson import json_util
from pymongo.server_api import ServerApi
import re
import os

def parse_json(data):
    return json.loads(json_util.dumps(data))

def getMongoDatabase():
    #db_username = os.environ['db_username'] 
    #db_password = os.environ['db_password']
    #uri = "mongodb+srv://" + db_username + ":" + db_password + "@anime-powerscale.gxqyxw1.mongodb.net/?authSource=admin"
    uri = os.environ['mongo_uri']
    client = MongoClient(uri, server_api=ServerApi('1'))
    #client = MongoClient("localhost", 27017)
    database = client["Dish"]

    return database

def insertIntoCollection(collectionName, obj):
    database = getMongoDatabase()
    collection = database[collectionName]
    doc = collection.insert_one(obj)
    return doc

def findManyFromCollection(collectionName, obj):
    database = getMongoDatabase()
    collection = database[collectionName]
    docsList = collection.find(obj)
    return parse_json(docsList)

def findOneFromCollection(collectionName, obj):
    database = getMongoDatabase()
    collection = database[collectionName]
    docsList = collection.find_one(obj)
    return parse_json(docsList)

def updateOne(collectionName, obj, query):
    database = getMongoDatabase()
    collection = database[collectionName]
    obj.pop('_id', None)
    obj = collection.replace_one(query, obj, True)
    return None

def getAggregationResults(aggregation, collectionName):
    database = getMongoDatabase()
    collection = database[collectionName]

    return collection.aggregate(aggregation)

def getAggregationResults(collectionName):
    database = getMongoDatabase()
    collection = database[collectionName]

    return collection.find()
