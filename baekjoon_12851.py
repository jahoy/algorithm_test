import sys
from collections import deque

input = sys.stdin.readline
n, k = map(int, input().split())
MAX_SIZE = 100001
VISIT, WAY = 0, 1
check = [[0, 0] for _ in range(MAX_SIZE)]


def bfs(start):
    q = deque([start])
    check[start][WAY] = 1
    while q:
        cur = q.popleft()
        for next_cur in (cur - 1, cur + 1, cur * 2):
            if 0 <= next_cur < MAX_SIZE:
                if check[next_cur][VISIT] == 0:
                    check[next_cur][VISIT] = check[cur][VISIT] + 1
                    check[next_cur][WAY] = check[cur][WAY]
                    q.append(next_cur)
                elif check[next_cur][VISIT] == check[cur][VISIT] + 1:
                    check[next_cur][WAY] += check[cur][WAY]

bfs(n)
print(check[k][VISIT])
print(check[k][WAY])