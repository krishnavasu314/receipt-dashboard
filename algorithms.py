# Placeholder for search, sort, and aggregation algorithms

def linear_search(records, keyword):
    return [r for r in records if keyword.lower() in str(r).lower()]

def quicksort(arr, key):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if key(x) <= key(pivot)]
    right = [x for x in arr[1:] if key(x) > key(pivot)]
    return quicksort(left, key) + [pivot] + quicksort(right, key)

def aggregate_sum(records, field):
    return sum(getattr(r, field) for r in records)






