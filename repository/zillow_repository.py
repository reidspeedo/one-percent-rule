import pymongo
import os

connection_string = os.environ.get("MONGO_DB_CONN_STR")
client = pymongo.MongoClient(connection_string)
db = client.zillowdb

def default_response(key = None):
    response = []
    for property in db.property.find(key):
        response.append(
            {
                "object_id": str(property["_id"]),
                "address": property["address"],
                "postal_code": property["postal_code"],
                "rent_estimate": property["rent_estimate"],
                "url": property["url"]
            }
        )
    return response


def create_property(property):
    id = db.property.insert(property)
    return default_response(key={"_id": id})
