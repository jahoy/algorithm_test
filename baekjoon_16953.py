# https://www.acmicpc.net/problem/16953

from collections import deque
a, b = map(int, input().split())

q = deque([(a, 1)])
res = -1
while q:
    new_num, cnt = q.popleft()
    if new_num == b:
        res = cnt
        break
    if new_num * 2 <= b:
        q.append((new_num * 2, cnt + 1))
    if int(str(new_num) + '1') <= b:
        q.append((int(str(new_num) + '1'), cnt + 1))
print(res)