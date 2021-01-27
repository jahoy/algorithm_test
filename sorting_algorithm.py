# 퀵정렬
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


# 합병정렬
def merge(left, right):
    merged = list()
    left_index, right_index = 0, 0
    
    # case 1: left/right 둘다 있을때
    while left_index < len(left) and right_index < len(right):
        if left[left_index] < right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    # case 2: left 데이터가 없을때
    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1
    
    # case 3: right 데이터가 없을때
    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1

    return merged


def mergesplit(data):
    if len(data) <= 1:
        return data

    medium = len(data) // 2
    left = mergesplit(data[:medium])
    right = mergesplit(data[medium:])
    return merge(left, right)

# 거품 정렬
def bubble_sort(data):
    for i in range(len(data) - 1):
        for index in range(len(data) - i - 1):
            if data[i] > data[i+1]:
                data[i], data[i+1] = data[i+1], data[i]
    return data


# 삽입 정렬
def insertion_sort(data):
    for i in range(len(data)-1):
        for index in range(i+1, 0, -1):
            if data[index] < data[index-1]:
                data[index], data[index-1] = data[index-1], data[index]
    return data


# 선택 정렬
def selection_sort(data):
    for stand in range(len(data)-1):
        lowest = stand
        for i in range(stand+1, len(data)):
            if data[lowest] > data[i]:
                lowest = i
        data[lowest], data[stand] = data[stand], data[lowest]