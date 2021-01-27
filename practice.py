def qsort(data):
    if len(data) <= 1:
        return data
    left, right = list(), list()
    pivot = data[0]

    for index in range(1, len(data)):
        if data[index] < pivot:
            left.append(data[index])
        else:
            right.append(data[index])

    return qsort(left) + [pivot] + qsort(right)