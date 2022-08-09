from turtle import xcor
import unittest
import find_duplicate
from unittest import mock
import numpy as np
from mongoengine import connect, disconnect
import mongomock
import pymongo 

class TestFindDuplicate(unittest.TestCase):
    # raises an exception while the test is running
    def setUp(self):
        self.fd = find_duplicate.FindDuplicate()
        self.arr = ["6", "3", "1", "9" , "22"]
        self.db = connect(db='mongotest', host='mongomock://localhost')

    def tearDown(self):
        disconnect()

    def test_hashed_title(self):
        self.assertEqual(self.fd.hashed_title("zugunglück von meerbusch - wie sicher ist bahnfahren?"), "231f")

    def test_non_vowels(self):
        self.assertEqual(self.fd.non_vowels("text/html"), "txth")

    def test_format_size(self):
        self.assertEqual(self.fd.non_vowels("10823381"), "108")

    def test_hybrid_quicksort(self):
        arr = ["234xdf", "234efg", "234efg", "ab534e", "ab534e", "ab524c", "5defoi"]
        sorted_arr = ["234efg", "234efg", "234xdf", "5defoi", "ab524c", "ab534e", "ab534e"]
        self.fd.hybrid_quicksort(arr,0, len(arr)-1)
        self.assertEqual(arr, sorted_arr)
    
    def test_insertionsort(self):
        print(self.fd.insertionsort(self.arr, 0, len(self.arr)-1))
        pass
        
    def test_partition(self):
        self.assertEqual(self.fd.partition(self.arr, 0, len(self.arr)-1), 1)

    def test_create_partition(self):
        arr = ["234xdf", "234efg", "234efg", "ab534e", "ab534e", "ab524c", "5defoi"]
        partitioned_arr = [['234xdf', '234efg', '234efg'], ['ab534e', 'ab534e', 'ab524c'], ['5defoi']]
        self.assertEqual(list(self.fd.create_partition(arr)), partitioned_arr)

    def test_partition_size(self):
        unsorted_arr = [["234xdf", "234efg"],["ab534e", "ab524c"],["5defoi"]]
        max_partition_size = self.fd.partition_size(unsorted_arr)
        self.assertEqual(max_partition_size, 2)

    def test_sorted_blocks(self): 
        partitioned_arr = np.array(["234efg", "234efg", "234xdf","5defoi", "ab524c", "ab534e", "ab534e"])
        noduplicate_arr = ['234efg', '234xdf', '5defoi', 'ab524c', 'ab534e']
        x = self.fd.sorted_blocks(partitioned_arr, 2, 3)
        self.assertListEqual(x.tolist(), noduplicate_arr)

    def delete_document(self):
        pass

if __name__ == '__main__':
    unittest.main()