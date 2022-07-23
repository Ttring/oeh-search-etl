import hashlib
import random
import time
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pymongo
from scipy.optimize import curve_fit

from converter import settings

'''
1: obtain documents from database
2: create key from metadata
3: sort metadata according to key
4: create partition according to key
5: implement sorted block algorithms 
'''

class FindDuplicate: 

    def __init__(self):
        # self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

        # access database on MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

        # key_list for sorting
        self.key_list_qh = [] # list for quick sort hybrid

    def create_sort_key(self):
        # filter off collection name "system.version" and save the rest as self.collection
        self.collection = self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne':  'system.version'}})
        # list every collection 
        for collection in self.collection: 
            if (collection == "sodix_spider"  or  collection =="test_spider"):
                print("Collection name: " +collection) 
                n = 0   
                # list every document in collection
                for document in self.db[collection].find():
                    #pprint(data)
                    if n  == 5:
                        break
                    try: 
                        size = document['lom']['technical']['duration']
                    except KeyError:
                        try:
                            size = document['lom']['technical']['size']
                        except KeyError:
                            size = "00"
                    try :
                        format = document['lom']['technical']['format']
                    except KeyError:
                        format = ""

                    # change title to small capital letters and combine it with it's format type
                    key = self.hashed_title(document['lom']['general']['title'].lower()) + self.non_vowels(format) + self.format_size(size)

                    # append key into key_list for merge sort
                    self.key_list_qh.append(key)

                    # insert key and collection as field into document
                    self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"sortKey": key}})
                    self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"spiderName": collection}})
                    n += 1
        self.sort_sortkey()

    def sort_sortkey(self):
        copy_key_list = list(self.key_list_qh) # make a original copy of the list
        self.hybrid_quick_sort(self.key_list_qh, 0 ,len(self.key_list_qh)-1)  # sort the sort-key 
        print("num\tvor Sortierung\tnach Sortierung")
        for i, (a, b) in enumerate(zip(copy_key_list, self.key_list_qh)):
            print(str(i) + '\t' +  a+ '\t' + b)
        self.create_partition(self.key_list_qh)

    def hashed_title(self, title):
        # hash the title for comparison purposes
        encoded_str = title.lower().encode()
        hash_obj_sha224 = hashlib.sha224(encoded_str)
        return hash_obj_sha224.hexdigest()[0:4]
    
    # convert MIME type to part of the key by getting it's non vowel alphabet such as application/pdf will be pplpdf
    def non_vowels(self, format):
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
    
    def format_size(self, size): 
        return str(size)[0:2]
        
    # Hybrid Quick Sort 
    def insertion_sort(self, list, low, n):    
        for i in range(low + 1, n + 1):
            pivot = list[i]
            while i>low and list[i-1]>pivot:
                list[i]= list[i-1]
                i-= 1
            list[i]= pivot
 
    def partition(self, list, low, high):
        pivot = list[high]
        i = j = low
        for i in range(low, high):
            if list[i]<pivot:
                list[i], list[j]= list[j], list[i]
                j+= 1
        list[j], list[high]= list[high], list[j]
        return j
         
    def hybrid_quick_sort(self, list, low, high):
        while low<high:
            # when the list has less than 10 elements, then run insertionsort. the threshold is self-defined.
            if high-low + 1<10:
                self.insertion_sort(list, low, high)
                break
            else:
                pivot = self.partition(list, low, high)
                if pivot-low<high-pivot: # hybrid sort left side (between low and pivot)
                    self.hybrid_quick_sort(list, low, pivot-1)
                    low = pivot + 1
                else: # hybrid sort right side (between pivot and high)
                    self.hybrid_quick_sort(list, pivot + 1, high)
                    high = pivot-1

    def create_partition(self, list):
        start_p = 0
        for i, sortkey in enumerate (list[:-1]):
            if sortkey == list[i+1]:
                end_p = i + 1
            else :
                start_p = i + 1 
                end_p = start_p
            print("start: " +str(start_p) +"\tend :" +str(end_p)) if (end_p is not start_p) else ""
        #for i in range(0, len(list), 2):
         #   yield list[i : i+2]


a = FindDuplicate()
a.create_sort_key()
