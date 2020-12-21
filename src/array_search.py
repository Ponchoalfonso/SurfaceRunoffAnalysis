def findIndex(arr, predicate):
    for idx, value in enumerate(arr):
        if predicate(value):
            return idx
    return -1


def find(arr, predicate):
    for value in arr:
        if predicate(value):
            return value
    return None


def findMany(arr, predicate):
    result = []
    for value in arr:
        if predicate(value):
            result.append(value)
    return result
