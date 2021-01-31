def qsort(data):
    if len(data) <= 1:
        return data

    pivot = data[0]
    left, right = list(), list()

    for i in range(1, len(data)):
        if i < pivot:
            left.append(data[i])
        else:
            right.append(data[i])

    return qsort(left) + [pivot] + qsort(right)



def merge(left, right):
    merged = list()
    l, r = 0, 0
    while l < len(left) and r < len(right):
        if left[l] < right[r]:
            merged.append(left[l])
            l += 1
        else:
            merged.append(right[r])
            r += 1

    if l < len(left):
        merged.extend(left[l:])
    if r < len(right):
        merged.extend(right[r:])

    return merged


def merge_split(data):
    if len(data) <= 1:
        return data
    
    medium = int(len(data) / 2)

    left  = merge_split(data[:medium])
    right = merge_split(data[medium:])
    return merge(left, right)