import pymongo
from converter import settings
from pprint import pprint

class find_duplicate: 

    def __init__(self):
        #self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

    def get_metadata(self):
        # access database on MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        # Filter off collection name "system.version" and save the rest as self.collection
        self.collection = self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne': 'system.version'}})
        
        for collection in self.collection:
            for data in self.db[collection].find():
                if data == "system.version":
                   continue
                print("Collection name: " +collection)    
                pprint(data)

a = find_duplicate()
a.get_metadata()