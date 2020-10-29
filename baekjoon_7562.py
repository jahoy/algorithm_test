# https://www.acmicpc.net/problem/7562

import sys
from collections import deque

dx = [-2, -1, 1, 2, 2, 1, -1, -2]
dy = [-1, -2, -2, -1, 1, 2, 2, 1]

input = sys.stdin.readline
T = int(input())

for _ in range(T):
    q = deque()
    size = int(input())
    x, y = map(int, input().split())
    cx, cy = map(int, input().split())

    q.append([x, y, 0])
    visited = [[False] * size for _ in range(size)]
    visited[y][x] = True
    while q:
        tx, ty, tt = q.popleft()
        if cx == tx and cy == ty:
            print(tt)
            break
        for i in range(8):
            if 0 <= tx + dx[i] < size and 0 <= ty + dy[i] < size and not visited[ty+dy[i]][tx+dx[i]]:
                q.append([tx+dx[i], ty+dy[i], tt+1])
                visited[ty+dy[i]][tx+dx[i]] = True