from ast import Delete
import hashlib
from multiprocessing.dummy import Array
import random
from re import A
from reprlib import aRepr
import time

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
6: delete duplicate data based on sort key
'''

class FindDuplicate:

    def __init__(self):
        # self.enabled = env.get("MODE", default="edu-sharing") == "edu-sharing"
        self.mongo_uri = settings.MONGO_URI
        self.mongo_db = settings.MONGO_DATABASE

        # access database on MongoDB
        self.client = pymongo.MongoClient(self.mongo_uri,  serverSelectionTimeoutMS = 2000)
        self.db = self.client[self.mongo_db]

         # array for sorting
        self.first_par_element = np.array([]) # first partition element
    
    def get_collection(self, define_collection):
        if (define_collection == "all") : 
            # filter off collection name "system.version" and save the rest as self.collection
            return self.db.list_collection_names(filter={'type': 'collection', 'name': {'$ne':  'system.version'}})
        elif(define_collection == "temp") : 
            # list specific collection for testing
            return ['test_spider', 'sodix_spider']
        elif(define_collection == "test"):
            # use only test_spider for testing
            return ['test_spider']

    def create_sortKey(self, collection):
        key_arr_qh = np.array([])
        
        # arr every collection 
        for x in collection: 
            print(x)
            for document in self.db[x].find():
                #   if n  == 10:
                #     break
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

                # append key into key_arr for hybrid-quicksort
                key_arr_qh = np.append(key_arr_qh, key)
        
                # insert key and collection as field into document
                self.db[x].update_one( {"_id": document["_id"]}, {"$set": {"sortKey": key}})
                self.db[x].update_one( {"_id": document["_id"]}, {"$set": {"spiderName": x}})
                # n += 1
        #print(key_arr_qh)
        return key_arr_qh

    def hashed_title(self, title):
        # hash the title for comparison purposes
        encoded_str = title.lower().encode()
        hash_obj_sha224 = hashlib.sha224(encoded_str)
        return hash_obj_sha224.hexdigest()[0:4]
    
    # convert MIME type to part of the key by getting it's non vowel alphabet such as application/pdf will be pplpdf
    def non_vowels(self, format):
        # split application/pdf to arr['application','pdf']
        arr = format.split('/')
        vowels = ('a','e','i','o','u')
        non_vowels = ""

        for word in arr:
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

        #sort based on first 3 characters of the sort key.
        for i in range(len(arr[:-1])): 
            if(arr[i][0:3] == arr[i+1][0:3]) :
                end_p = i + 1
            else:    
                #print("start: " +str(start_p) +"\tend :" +str(end_p)) 
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
        lcr = [] # arr comparison records (elements in the window) 
        window_num = o + 1 # num of window in overlapping area
        i = 0
        #sorted_arr = arr(sorted_arr)
        # iterate over all records to search for duplicates
        while i<len(sorted_arr):
            
            # if it is first element of the partition 
            if (i in self.first_par_element and i>0) or (len(lcr) == max_partition_size): 
                # remove all records of the previous partition that is not in overlap
                while len(lcr) > o:
                    lcr.pop(0)   
                window_num = 0
            # if window is less than overlap size
            elif window_num <= o :
                lcr.pop(0)
                #print("lcr:" , lcr)
                window_num += 1
         
            # compare current record with all records in lcr/window
            for j in range(len(lcr)): 
                #if (sorted_arr[i]== lcr[j]) and sorted_arr.count(lcr[j])>1:
                if (sorted_arr[i]== lcr[j]) and sorted_arr.tolist().count(lcr[j])>1:
                    self.delete_document(sorted_arr[i], collection)
                    #sorted_arr.pop(i)
                    sorted_arr = np.delete(sorted_arr, i)
                    i-=1
                    #print("sorted arr after popping 1 record out :\n", sorted_arr)               
                else:         
                    continue
            
            if len(lcr) == max_partition_size:
                lcr.pop(0)

            lcr.append(sorted_arr[i])
            i += 1 
        return sorted_arr
    
    def delete_document(self, sortKey, collection):
        count = 0
        for x in collection:            
            if (count == 0):
                #print(x + sortKey)
                self.db[x].delete_one({'sortKey': sortKey})
                count += 1
            else:
                break

a = FindDuplicate()
# collection = a.get_collection('temp')
# sort_keylist = a.create_sortKey(collection)
# a.hybrid_quicksort(sort_keylist, 0 ,len(sort_keylist)-1)  # sort the sort-key 
# sorted_keylist = sort_keylist
# p = a.create_partition(sorted_keylist)
# max_size = a.partition_size(p)
# print(a.sorted_blocks(sorted_keylist, 2 ,max_size, collection))
