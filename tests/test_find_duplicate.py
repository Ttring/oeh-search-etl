
import unittest
import find_duplicate
import numpy as np
import time
from pymongo import errors

class TestFindDuplicate(unittest.TestCase):
    # raises an exception while the test is running
    def setUp(self):
        self.fd = find_duplicate.FindDuplicate()

    # check if MongDB server is running
    def test_mongoDB_connection(self):
        start = time.time()
        try: 
            # raise an exception to see if the instance is true
            client = self.fd.client
            client.server_info()
            #print ("server_info():", client.server_info())
        except:
            print("Connection Error")
            print(time.time() - start)
            client = None
            return client

    def test_database_collection(self):
        # test collection by calling a document
        col = self.fd.db["test_spider"]

        try:
            doc= col.find_one()
            #print ("nfind_one():", doc)
        except errors.ServerSelectionTimeoutError as err:
            print ("nfind_one() ERROR:", err)

    def test_create_sortKey(self):
        self.assertTrue(len(self.fd.create_sortKey()))
        
    def test_hashed_title(self):
        self.assertEqual(self.fd.hashed_title("zugunglück von meerbusch - wie sicher ist bahnfahren?"), "231f")

    def test_non_vowels(self):
        self.assertEqual(self.fd.non_vowels("text/html"), "txth")

    def test_format_size(self):
        self.assertEqual(self.fd.non_vowels("10823381"), "108")

    def test_hybrid_quicksort(self):
        # sort key using hybridsort. 
        arr = ["234xdf", "234efg", "234efg", "ab534e", "ab534e", "ab524c", "5defoi"]
        sorted_arr = ["234efg", "234efg", "234xdf", "5defoi", "ab524c", "ab534e", "ab534e"]
        self.fd.hybrid_quicksort(arr,0, len(arr)-1)
        self.assertEqual(arr, sorted_arr)
    
    def test_insertionsort(self):
        # sort number in list.
        arr = [3, 10, 25, 23, 2]
        sorted_arr = [ 2, 3, 10, 23, 25]
        self.fd.insertionsort(arr, 0, len(arr)-1)
        after_arr = arr
        self.assertEqual(sorted_arr, after_arr)
        
    def test_partition(self):
        # partition is created using middle point, so it should return 1 if it is correct. 
        arr = ["6", "3", "1", "9" , "22"]
        self.assertEqual(self.fd.partition(arr, 0, len(arr)-1), 1)

    def test_create_partition(self):
        # test if the partition is created correctly based on the first 3 symbol in sortkey.
        arr = ["234xdf", "234efg", "234efg", "ab534e", "ab534e", "ab524c", "5defoi"]
        partitioned_arr = [['234xdf', '234efg', '234efg'], ['ab534e', 'ab534e', 'ab524c'], ['5defoi']]
        self.assertEqual(list(self.fd.create_partition(arr)), partitioned_arr)

    def test_partition_size(self):
        # test if it returns the maximum size from array correctly. 
        unsorted_arr = [["234xdf", "234efg"],["ab534e", "ab524c"],["5defoi"]]
        max_partition_size = self.fd.partition_size(unsorted_arr)
        self.assertEqual(max_partition_size, 2)

    def test_sorted_blocks(self): 
        # compare if the block is sorted (elimate duplicate in the same block)
        partitioned_arr = np.array(["234efg", "234efg", "234xdf","5defoi", "ab524c", "ab534e", "ab534e"])
        noduplicate_arr = ['234efg', '234xdf', '5defoi', 'ab524c', 'ab534e']
        x = self.fd.sorted_blocks(partitioned_arr, 2, 3)
        self.assertListEqual(x.tolist(), noduplicate_arr)

    def test_delete_document(self):
        try : 
            # find SortKey from first document.
            first_document = self.fd.db['test_spider'].find_one()['sortKey']

            # test if SortKey exists 
            x = self.fd.db['test_spider'].find_one({"sortKey": first_document})
            self.assertTrue(x)

            # delete based on SortKey. Return False if it couldnt find that particular document.
            self.fd.delete_document(first_document)
            x = self.fd.db['test_spider'].find_one({"sortKey": first_document})
            self.assertFalse(x)

            # test with false SortKey.
            y = self.fd.db['test_spider'].find_one({"sortKey": "23433434"})
            self.assertFalse(y)

        except TypeError:
            print("test_spider is empty, Test_spider needs to be executed.")

if __name__ == '__main__':
    unittest.main()