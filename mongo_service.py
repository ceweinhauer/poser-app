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
    database = client["AnimePS"]

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

def get_rankings(rankingParams):
    pattern = re.compile(rf"^{rankingParams['searchFilter']}.*" , re.IGNORECASE)
    aggregation = []

    if rankingParams['animeFilter']:
        aggregation.append({"$match":{"Primary Assignment": rankingParams['animeFilter']}})

    if rankingParams['searchFilter']:
        aggregation.append({"$match": {"$or":[{"Name": pattern},
                                              {"Primary Assignment": pattern}, 
                                              {"Other Names": pattern}, 
                                              {"Tags": pattern},]}})
    aggregation.append({"$sort":{"score": -1}})

    if rankingParams['pageNumber'] and rankingParams['pageNumber'] > 1:
        skipAmount = (rankingParams['pageNumber'] - 1) * rankingParams['pageSize']
        aggregation.append({"$skip":skipAmount})

    if rankingParams['pageSize'] and rankingParams['pageSize'] > 1:
        limitAmount = rankingParams['pageSize']
        aggregation.append({"$limit":limitAmount})

    aggregation.append({"$project": {"ID": 0,"link": 0,"details": 0, "_id": 0}})

    database = getMongoDatabase()
    collection = database["Characters"]

    results = collection.aggregate(aggregation)
    return parse_json(results)

def get_battles_results(rankingParams):
    pattern = re.compile(rf"^{rankingParams['searchFilter']}.*" , re.IGNORECASE)
    aggregation = []

    if rankingParams['animeFilter']:
        aggregation.append({"$match": {"$or":[{"fighter1.Primary Assignment": rankingParams['animeFilter']},
                                              {"fighter2.Primary Assignment": rankingParams['animeFilter']}]}})

    if rankingParams['searchFilter']:
        aggregation.append({"$match": {"$or":[{"fighter1.Name": pattern},
                                              {"fighter1.Primary Assignment": pattern}, 
                                              {"fighter1.Other Names": pattern}, 
                                              {"fighter1.Tags": pattern},
                                              {"fighter2.Name": pattern},
                                              {"fighter2.Primary Assignment": pattern}, 
                                              {"fighter2.Other Names": pattern}, 
                                              {"fighter2.Tags": pattern},]}})

    if rankingParams['pageNumber'] and rankingParams['pageNumber'] > 1:
        skipAmount = (rankingParams['pageNumber'] - 1) * rankingParams['pageSize']
        aggregation.append({"$skip":skipAmount})

    if rankingParams['pageSize'] and rankingParams['pageSize'] > 1:
        limitAmount = rankingParams['pageSize']
        aggregation.append({"$limit":limitAmount})

    database = getMongoDatabase()
    collection = database["Battles"]

    results = collection.aggregate(aggregation)
    return parse_json(results)

def get_top_100_chacters():
    aggregation = []
    aggregation.append({"$sort":{"score": -1}})
    aggregation.append({"$limit":100})
    aggregation.append({"$project": {"link": 0,"details": 0, "_id": 0}})

    database = getMongoDatabase()
    collection = database["Characters"]

    results = collection.aggregate(aggregation)
    return parse_json(results)

def get_top_10_chacters(count):
    aggregation = []
    aggregation.append({"$sort":{"score": -1}})
    aggregation.append({"$limit":int(count)*2})
    aggregation.append({"$project": {"link": 0,"details": 0, "_id": 0}})

    database = getMongoDatabase()
    collection = database["Characters"]

    results = collection.aggregate(aggregation)
    return parse_json(results)

def get_animes_list():
    database = getMongoDatabase()
    collection = database["Characters"]

    results = collection.distinct("Primary Assignment")
    return parse_json(results)

def get_10_closest_characters(scoreValue, count):
    aggregation = []
    aggregation.append({"$addFields":{"value": {"$abs": {"$subtract": [scoreValue, "$score"]}}}})
    aggregation.append({"$sort":{"value": -1}})
    aggregation.append({"$limit":int(count)*2})
    aggregation.append({"$project": {"link": 0,"details": 0, "_id": 0}})
    database = getMongoDatabase()
    collection = database["Characters"]

    results = collection.aggregate(aggregation)
    return parse_json(results)