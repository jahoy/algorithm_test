# https://www.acmicpc.net/problem/1012

import sys
sys.setrecursionlimit(50000)
input = sys.stdin.readline

dx = (-1, 1, 0, 0)
dy = (0, 0, -1, 1)


def dfs(x, y):
    visited[y][x] = True
    for i in range(4):
        nx = x + dx[i]
        ny = y + dy[i]
        if 0 <= nx < M and 0 <= ny < N and not visited[ny][nx] and matrix[ny][nx] == 1:
            dfs(nx, ny)

T = int(input())
for _ in range(T):
    M, N, K = map(int, input().split())
    count = 0
    matrix = [[0]*50 for _ in range(50)]
    visited = [[False]*50 for _ in range(50)]
    for _ in range(K):
        x, y = map(int, input().split())
        matrix[y][x] = 1
    for y in range(N):
        for x in range(M):
            if matrix[y][x] == 1 and not visited[y][x]:
                dfs(x, y)
                count +=1
    print(count)

