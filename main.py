import find_duplicate

if __name__ == "__main__":
    a = find_duplicate.FindDuplicate()
    collection = a.get_collection('test')
    sort_keylist = a.create_sortKey(collection)
    a.hybrid_quicksort(sort_keylist, 0 ,len(sort_keylist)-1)  # sort the sort-key 
    sorted_keylist = sort_keylist
    p = a.create_partition(sorted_keylist)
    max_size = a.partition_size(p)
    a.sorted_blocks(sorted_keylist, 2 ,max_size, collection)
    print("total deleted documents : " , a.deleted_document)