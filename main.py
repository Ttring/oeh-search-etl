import find_duplicate
from collections import Counter

if __name__ == "__main__":
    list = []
    a = find_duplicate.FindDuplicate()
    collection = a.get_collection('temp')
    sort_keylist = a.create_sortKey(collection)
    a.hybrid_quicksort(sort_keylist, 0 ,len(sort_keylist)-1)  # sort the sort-key 
    sorted_keylist = sort_keylist
    print("Vor Sortierung")
    print(sorted_keylist)
    counter = a.counter(sorted_keylist, collection)
    for key, value in counter.items():
        list.append(key)
    print("Nach Sortierung")
    print(list)
    # p = a.create_partition(sorted_keylist)
    # max_size = a.partition_size(p)
    # a.sorted_blocks(sorted_keylist, 2 ,max_size, collection)
    print("total deleted documents with counter : " , a.deleted_document)