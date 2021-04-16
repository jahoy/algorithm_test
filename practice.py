import sys
input = sys.stdin.readline

N, S = map(int, input().split())
arr = list(map(int, input().split()))

ans = 0

def dfs(index, total):
    global ans
    if index == N:
        return
    if total + arr[index] == S:
        ans += 1
    dfs(index + 1, total)
    dfs(index + 1, total + arr[index])

dfs(0, 0)
print(ans)