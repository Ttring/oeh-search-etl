import hashlib
from pprint import pprint

import pymongo

from converter import settings

'''
1: obtain documents from database
2: create key from metadata
3: sort metadata according to key
4: implement sorted block algorithms 
'''

class find_duplicate: 

    def __init__(self):
        #self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

    def create_key(self):
        # access database on MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        # Filter off collection name "system.version" and save the rest as self.collection
        self.collection = self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne': 'system.version'}})
        
        # print out all documents in every collection 
        for collection in self.collection:
            for data in self.db[collection].find():
                if data == "system.version":
                   continue
                print("Collection name: " +collection)    
                #pprint(data)
                key = self.hashing(data['lom']['general']['title']) + self.get_non_vowels(data['lom']['technical']['format'])
                print(key)

    def hashing(self, title):
        # hash the string for comparison purposes
        encoded_str = title.encode()
        hash_obj_sha224 = hashlib.sha224(encoded_str)
        return hash_obj_sha224.hexdigest()
    
    # convert MIME type to part of the key by getting it's non vowel alphabet such as application/pdf will be pplpdf
    def get_non_vowels(self, format):
        # split application/pdf to list['application','pdf']
        list = format.split('/')
        vowels = ('a','e','i','o','u')
        non_vowels = ""

        for word in list:
            # n act as a breakpoint. It stops after getting 3 non vowels.
            n = 0
            for alphabet in word.lower():
                if n == 3:
                    break
                if alphabet in vowels:
                    word = word.replace(alphabet,"")
                else:
                    n += 1
            non_vowels += word[0:3]
        return non_vowels


a = find_duplicate()
a.create_key()
