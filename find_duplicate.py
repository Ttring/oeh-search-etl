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
4: implement sorted block algorithms 
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
        self.collection = self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne': 'system.version'}})

        # list every collection 
        for collection in self.collection:
            print("Collection name: " +collection)   
            #n = 0
            # list every document in collection
            for document in self.db[collection].find():
                #pprint(data)
                #if n == 1000: 
                 #   break
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
                #n += 1
        self.sort_sort_key()

    def sort_sort_key(self):
        print("inside sort key")
        copy_key_list = list(self.key_list_qh) # make a original copy of the list
        self.hybrid_quick_sort(self.key_list_qh, 0 ,len(self.key_list_qh)-1)  # sort the sort-key 
        print("num\t\tkey_list_qh")
        for i in range(len(self.key_list_qh)):
            print(str(i) + '\t' +  copy_key_list[i]+ '\t' + self.key_list_qh[i])

    def hashed_title(self, title):
        # hash the title for comparison purposes
        encoded_str = title.encode()
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
    def insertion_sort(self, arr, low, n):    
        for i in range(low + 1, n + 1):
            pivot = arr[i]
            while i>low and arr[i-1]>pivot:
                arr[i]= arr[i-1]
                i-= 1
            arr[i]= pivot
 
    def partition(self, arr, low, high):
        pivot = arr[high]
        i = j = low
        for i in range(low, high):
            if arr[i]<pivot:
                arr[i], arr[j]= arr[j], arr[i]
                j+= 1
        arr[j], arr[high]= arr[high], arr[j]
        return j
         
    def hybrid_quick_sort(self, arr, low, high):
        while low<high:
            if high-low + 1<10:
                self.insertion_sort(arr, low, high)
                break
            else:
                pivot = self.partition(arr, low, high)
                if pivot-low<high-pivot: # hybrid sort left side (between low and pivot)
                    self.hybrid_quick_sort(arr, low, pivot-1)
                    low = pivot + 1
                else: # hybrid sort right side (between pivot and high)
                    self.hybrid_quick_sort(arr, pivot + 1, high)
                    high = pivot-1

a = FindDuplicate()
a.create_sort_key()

# temp = [1,4,3,5,6,23,8,9,13,15,23,7,2]
# a.hybrid_quick_sort(temp, 0 , len(temp)-1)
# print(temp)