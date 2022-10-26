import find_duplicate
from collections import Counter

if __name__ == "__main__":
    a = find_duplicate.FindDuplicate()

    collection = a.get_collection('temp')
    sort_keylist = a.create_sortKey(collection)
    
    counter = a.counter(sort_keylist, collection)
    
    #p = a.create_partition(sorted_keylist)
    #max_size = a.partition_size(p)
    #a.sorted_blocks(sorted_keylist, 2 ,max_size, collection)
  
    print("total deleted documents with counter : " , a.deleted_document)