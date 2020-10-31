# https://www.acmicpc.net/problem/14888
import sys
input = sys.stdin.readline

N = int(input())
nums = list(map(int, input().split()))
add, sub, mul, div = map(int, input().split())

max_ = -1e9
min_ = 1e9

def dfs(cnt, res, add, sub, mul, div):
    global max_, min_
    if cnt == N:
        max_ = max(res, max_)
        min_ = min(res, min_)
        return
    if add:
        dfs(cnt+1, res+nums[cnt], add-1, sub, mul, div)
    if sub:
        dfs(cnt+1, res-nums[cnt], add, sub-1, mul, div)
    if mul:
        dfs(cnt+1, res*nums[cnt], add, sub, mul-1, div)
    if div:
        dfs(cnt+1, int(res / nums[cnt]), add, sub, mul, div-1)

dfs(1, nums[0], add, sub, mul, div)
print(max_)
print(min_)