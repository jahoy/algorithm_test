#https://www.acmicpc.net/problem/15649

import sys
input = sys.stdin.readline

N, M  = map(int, input().split())

check = [False] * (N+1)
arr = []

def solve(depth, N, M):
    if depth == M:
        print(' '.join(map(str, arr)))
        return
    for i in range(1, N+1):
        if check[i]:
            continue
        check[i] = True
        arr.append(i)
        solve(depth+1, N, M)
        check[i] = False
        arr.pop()

solve(0, N, M)
