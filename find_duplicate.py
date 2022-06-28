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
        # self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

        # access database on MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        # key_list for sorting
        self.key_list = []
        self.copy_key_list = []

    def create_sort_key(self):
        # filter off collection name "system.version" and save the rest as self.collection
        self.collection = self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne': 'system.version'}})
        
        # list every collection 
        for collection in self.collection:
            print("Collection name: " +collection)   

            # list every document in collection
            for document in self.db[collection].find():
                #pprint(data)
                try: 
                    size = document['lom']['technical']['duration']
                except KeyError:
                    size = document['lom']['technical']['size']

                # change title to small capital letters and combine it with it's format type
                key = self.get_hashed_title(document['lom']['general']['title'].lower()) + self.get_non_vowels(document['lom']['technical']['format']) + self.get_format_size(size)

                # append key into key_list for merge sort
                self.key_list.append(key)

                # insert key and collection as field into document
                self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"sortKey": key}})
                self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"spiderName": collection}})

        self.copy_key_list = list(self.key_list)
        self.merge_sort(self.copy_key_list, self.key_list, 0, len(self.key_list))
        print(self.key_list)

                   
    def get_hashed_title(self, title):
        # hash the title for comparison purposes
        encoded_str = title.encode()
        hash_obj_sha224 = hashlib.sha224(encoded_str)
        return hash_obj_sha224.hexdigest()[0:4]
    
    # convert MIME type to part of the key by getting it's non vowel alphabet such as application/pdf will be pplpdf
    def get_non_vowels(self, format):
        # split application/pdf to list['application','pdf']
        list = format.split('/')
        vowels = ('a','e','i','o','u')
        non_vowels = ""

        for word in list:
            # n acts as a breakpoint. It stops after getting 3 non vowels.
            n = 0
            for alphabet in word.lower():
                if n == 3:
                    break
                if alphabet in vowels:
                    word = word.replace(alphabet,"")
                else:
                    n += 1
            non_vowels += word[0:3]
        return non_vowels[0:4]
    
    def get_format_size(self, size): 
        return str(size)[0:2]

    def merge_sort(self, key_list, key_list_final, start, end):
         if end - start < 2:
             return
         if end - start == 2:
             if key_list_final[start] > key_list_final[start+1]:
                 key_list_final[start],key_list_final[start+1] = key_list_final[start+1],key_list_final[start]
             return
         mid = (end + start) // 2
         self.merge_sort(key_list_final, key_list, start, mid)
         self.merge_sort (key_list_final, key_list, mid, end)
           
         i = start
         j = mid
         idx = start
         while idx < end:
             if j >= end or ( i < mid and key_list[i] < key_list[j]):
                 key_list_final[idx] = key_list[i]
                 i += 1
             else:
                 key_list_final[idx] = key_list[j]
                 j += 1
             idx += 1

a = find_duplicate()
a.create_sort_key()

# b = [54,26,93,17,77,31,44,55,20]
# copylist = list(b)
# result = a.merge_sort(copylist, b, 0 , len(b))
# print(copylist)
# print(b)