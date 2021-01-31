letters = []
l, r = 0, len(letters) - 1

while l < r:
    mid = (l + r ) // 2
    if target < letters[mid]:
        r = mid
    elif target >= letters[mid]:
        l = mid + 1

return letters[r]