import pymongo
from converter import settings
from pprint import pprint

class find_duplicate: 

    def __init__(self):
        #self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

    def get_metadata(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        self.collection = self.db.list_collection_names()
        for i in range (len(self.collection)):
            print("Collection name: " +self.collection[i])
            collection = self.db[self.collection[i]]
            for data in collection.find():
                pprint(data) 

a = find_duplicate()
a.get_metadata()