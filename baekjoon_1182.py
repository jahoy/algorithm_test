#  https://www.acmicpc.net/problem/1182

import sys
input = sys.stdin.readline

N, S  = map(int, input().split())
arr = list(map(int, input().split()))

ans = 0

def dfs(index, total):
    global ans
    if index == N:
        return
    if total + arr[index] == S:
        ans += 1
    
    dfs(index + 1, total) # 더하지 않는 경우
    dfs(index + 1, total + arr[index]) # 더하는 겨우

dfs(0, 0)
print(ans)