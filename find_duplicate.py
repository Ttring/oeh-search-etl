import hashlib
import logging
import random
import time
from ast import Delete
from multiprocessing.dummy import Array
from re import A
from reprlib import aRepr

import matplotlib.pyplot as plt
import numpy as np
import pymongo
from scipy.optimize import curve_fit

from converter import settings

class FindDuplicate:

    def __init__(self):
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

        self.client = pymongo.MongoClient(self.mongo_uri,  serverSelectionTimeoutMS = 2000)
        self.db = self.client[self.mongo_db]

        self.first_par_element = np.array([]) # first partition element
        self.deleted_document = 0
    
    def get_collection(self, define_collection):
        if (define_collection == "all") : 
            return self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne':  'system.version'}})
        elif(define_collection == "temp") : 
            return ['sodix_spider', 'test_spider']
        elif(define_collection == "test"):
            return ['test_spider']

    def create_sortKey(self, collection):
        key_arr_qh = np.array([])
        n = 0
        for x in collection: 
            print(x)
            for document in self.db[x].find():

                try: 
                    size = document['lom']['technical']['duration']
                except KeyError:
                    try:
                        size = document['lom']['technical']['size']
                    except KeyError:
                        size = "00"

                try :
                    format = document['lom']['technical']['format']
                except :
                    format =  document['thumbnail']['mimetype'] 
  
                key = self.hashed_title(document['lom']['general']['title'].lower()) + self.MIME_type(format) + str(size)
                key_arr_qh = np.append(key_arr_qh, key)
        
                self.db[x].update_one( {"_id": document["_id"]}, {"$set": {"sortKey": key}})
                
        return key_arr_qh

    def hashed_title(self, title):
        encoded_str = title.lower().encode()
        hash_obj_sha224 = hashlib.sha224(encoded_str)
        return hash_obj_sha224.hexdigest()[0:4]
    
    # convert MIME type to part of the key by getting first 3 non-vowel before and after backslash.
    def MIME_type(self, format):
        # split application/pdf to arr['application','pdf']
        arr = format.split('/')
        vowels = ('a','e','i','o','u')
        non_vowels = ""

        for word in arr:
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
        
    def hybrid_quicksort(self, arr, low, high):
        while low<high:
            # when the arr has less than 10 elements, then run insertionsort. the threshold is self-defined.
            if high-low + 1<10:
                self.insertionsort(arr, low, high)
                break
            else:
                pivot = self.partition(arr, low, high)
                if pivot-low<high-pivot: # hybrid sort left side (between low and pivot)
                    self.hybrid_quicksort(arr, low, pivot-1)
                    low = pivot + 1
                else: # hybrid sort right side (between pivot and high)
                    self.hybrid_quicksort(arr, pivot + 1, high)
                    high = pivot-1

    def insertionsort(self, arr, low, high):    
        for i in range(low + 1, high + 1):
            pivot = arr[i]
            while i>low and arr[i-1]>pivot:
                arr[i]= arr[i-1]
                i-= 1
            arr[i]= pivot

    # returns middle pivot point
    def partition(self, arr, low, high):
        pivot = arr[high]
        i = j = low
        for i in range(low, high):
            if arr[i]<pivot:
                arr[i], arr[j]= arr[j], arr[i]
                j+= 1
        arr[j], arr[high]= arr[high], arr[j]
        return j
         
    def create_partition(self, arr):
        start_p = 0
        end_p = 0

        for i in range(len(arr[:-1])): 
            if(arr[i][0:3] == arr[i+1][0:3]) :
                end_p = i + 1
            else:    
                self.first_par_element = np.append(self.first_par_element, start_p) # save first element in partition
                yield arr[start_p : end_p +1] 
                start_p = i + 1 
                end_p = start_p
        self.first_par_element = np.append(self.first_par_element, start_p)
        yield arr[start_p : end_p +1]  

    def partition_size(self, arr):
        max_partition_size = 0

        for i in arr: 
            if(len(i)> max_partition_size):
                max_partition_size = len(i)
        return max_partition_size

    def sorted_blocks(self,sorted_arr,o,max_partition_size, collection) -> np.ndarray:
        lcr = [] 
        window_num = o + 1 
        i = 0
        
        while i<len(sorted_arr):
            
            if (i in self.first_par_element and i>0) or (len(lcr) == max_partition_size): 
                while len(lcr) > o:
                    lcr.pop(0)   
                window_num = 0

            elif window_num <= o :
                lcr.pop(0)
                window_num += 1
         
            for j in range(len(lcr)): 
                if (sorted_arr[i]== lcr[j]) and sorted_arr.tolist().count(lcr[j])>1:
                    self.delete_document(sorted_arr[i], collection)
                    
                    sorted_arr = np.delete(sorted_arr, i)
                    i-=1             
                else:         
                    continue

            lcr.append(sorted_arr[i])
            i += 1 

        return sorted_arr
    
    def delete_document(self, sortKey, collection):
        count = 0
        for x in collection:            
            if (count == 0):
                self.db[x].delete_one({'sortKey': sortKey})
                break
        self.deleted_document += 1