import unittest
from find_duplicate import FindDuplicate

class TestFindDuplicate(unittest.TestCase):
    # raises an exception while the test is running
    def setUp(self):
        self.fd = FindDuplicate()

   # @patch("patch.to.out.file.DBConnection")
    def test_create_sortKey(self):
        pass

    def test_sort_sortKey(self):
        pass

    def test_hashed_title(self):
        self.assertEqual(self.fd.hashed_title("zugunglück von meerbusch - wie sicher ist bahnfahren?"), "231f")

    def test_non_vowels(self):
        self.assertEqual(self.fd.non_vowels("text/html"), "txth")

    def test_format_size(self):
        self.assertEqual(self.fd.non_vowels("10823381"), "108")

    def test_hybrid_quicksort(self):
        pass
    def test_insertionsort(self):
        pass
    def test_partition(self):
        pass
    def test_create_partition(self):
        pass
    def test_partition_size(self):
        pass
    def test_sorted_blocks(self):
        pass
    def delete_document(self):
        pass

if __name__ == '__main__':
    unittest.main()