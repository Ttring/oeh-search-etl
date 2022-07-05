import hashlib
import time
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pymongo

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
        self.key_list_m = [] # list for merge sort
        self.key_list_qh = [] # list for quick sort hybrid
        self.key_list_q = [] # list for quick sort

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
                        size = "0"
                try :
                    format = document['lom']['technical']['format']
                except KeyError:
                    format = ""

                # change title to small capital letters and combine it with it's format type
                key = self.hashed_title(document['lom']['general']['title'].lower()) + self.non_vowels(format) + self.format_size(size)

                # append key into key_list for merge sort
                self.key_list_m.append(key)
                self.key_list_qh.append(key)
                self.key_list_q.append(key)

                # insert key and collection as field into document
                self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"sortKey": key}})
                self.db[collection].update_one( {"_id": document["_id"]}, {"$set": {"spiderName": collection}})
                #n += 1
        self.compare_sort()

    def compare_sort(self):
        time_merge = []
        time_quick = []
        time_hybrid = []
        num_data = []
        
        for i in range(100, 9900, 100):
            # create x-axis
            num_data.append(i)

            # create y-axis for merge sort
            key_list_m1 = self.key_list_m[0:i] #to limit the number of Metadata
            copy_key_list_m = list(key_list_m1)
            st = time.time()
            self.merge_sort(copy_key_list_m, key_list_m1, 0, len(key_list_m1))
            et = time.time()
            tm = et-st
            time_merge.append(tm)

            # create y-axis for hybrid quick sort
            key_list_qh1 = self.key_list_qh[0:i]
            st2 = time.time()
            self.hybrid_quick_sort(key_list_qh1, 0 ,len(key_list_qh1)-1)  
            et2 = time.time()     
            th = et2-st2
            time_hybrid.append(th)

            # create y-axis for quick sort
            key_list_q1 = self.key_list_q[0:i]
            st3 = time.time()
            self.quick_sort(key_list_q1, 0 ,len(key_list_q1)-1)       
            et3 = time.time()
            tq = et3-st3
            time_quick.append(tq)

            print("{}, {}, {}, {} ".format(i, tm, th, tq ))
        
        #print(self.key_list_m1)
        #print(self.key_list_qh1)
        #print(self.key_list_q1)

        #plt.plot(num_data, time_merge, label = "Merge Sort")

        m, c = np.polyfit(num_data, time_hybrid, 1)
        plt.plot(num_data, m*np.array(num_data)+c)
        plt.scatter(num_data, time_hybrid, label = "Hybrid Quick Sort", s = 2)
        #plt.plot(num_data, time_hybrid, label = "Hybrid Quick Sort")
        m1, c1 = np.polyfit(num_data, time_quick, 1)
        plt.plot(num_data, m1*np.array(num_data)+c1)
        plt.scatter(num_data, time_quick, label = "Quick Sort", s= 2)
        #plt.plot(num_data, time_quick, label = "Quick Sort")
        
        plt.xlabel("Anzahl der Metadaten")
        plt.ylabel("Ausführungszeit")
        plt.grid()
        plt.legend()
        plt.savefig("Compare_2.jpg")
               
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
    
    # Merge Sort
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
        

    # Hybrid Quick Sort 
    def insertion_sort(self, arr, low, n):
        for i in range(low + 1, n + 1):
            val = arr[i]
            j = i
            while j>low and arr[j-1]>val:
                arr[j]= arr[j-1]
                j-= 1
            arr[j]= val
 
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
    
                if pivot-low<high-pivot:
                    self.hybrid_quick_sort(arr, low, pivot-1)
                    low = pivot + 1
                else:
                    self.hybrid_quick_sort(arr, pivot + 1, high)
                    high = pivot-1
    
    # Quick Sort
    def quick_sort(self, arr, low, high):
        
        if low<high:
            pivot = self.partition1(arr, low, high)
            self.quick_sort(arr, low, pivot-1)
            self.quick_sort(arr, pivot + 1, high)
            return arr
  
    
    def partition1(self, arr, low, high):
        pivot = arr[high]
        i = j = low
        for i in range(low, high):
            if arr[i]<pivot:
                arr[i], arr[j]= arr[j], arr[i]
                j+= 1
        arr[j], arr[high]= arr[high], arr[j]
        return j

a = FindDuplicate()
a.create_sort_key()
