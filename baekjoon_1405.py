# https://www.acmicpc.net/problem/1405

import sys
input = sys.stdin.readline
sys.setrecursionlimit(100000)

N, p_e, p_w, p_s, p_n = map(int, input().split())

p = [p_e/100, p_w/100, p_s/100, p_n/100]
dx = [0, 0 , -1, 1]
dy = [-1, 1, 0, 0]
ans = 0

def dfs(x, y, length, prob, visited):
    global ans
    if length == N:
        if len(set(visited)) == N+1:
            ans += prob
        return
    for i in range(4):
        nx = x + dx[i]
        ny = y + dy[i]
        if (nx, ny) not in visited:
            visited.append((nx, ny))
            dfs(nx, ny, length+1, prob*p[i], visited)
            visited.pop() # 백트래킹

dfs(0, 0, 0 ,1, [(0, 0)])
print('{:.10f}'.format(ans))
