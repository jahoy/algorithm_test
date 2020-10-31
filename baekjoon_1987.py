# https://www.acmicpc.net/problem/1987
# 시간 초과 퓨ㅠ

import sys
sys.setrecursionlimit(1000000)
input = sys.stdin.readline

dx = [0, 0, 1, -1]
dy = [-1, 1, 0, 0]

R, C = map(int, input().split())
matrix = [list(map(lambda x: ord(x) - 65, input())) for _ in range(R)]
visited = [False] * 26 # 알파벳 26개만큼 배열 설정

def dfs(x, y, cnt):
    global answer
    answer = max(answer, cnt)
    visited[matrix[y][x]] = True
    for i in range(4):
        nx = x + dx[i]
        ny = y + dy[i]
        if(0 <= ny < R) and (0 <= nx < C) and not visited[matrix[ny][nx]]:
            dfs(nx, ny, cnt+1)
            visited[matrix[ny][nx]] = False


answer = 1
dfs(0, 0, answer)

print(answer)