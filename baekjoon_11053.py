# https://www.acmicpc.net/problem/11053

import sys

n = int(sys.stdin.readline())
array = list(map(int, sys.stdin.readline().split()))
dp = [1] * n
# dp[i] = array[i] 를 마지막 원소로 가지는 부분수열의 최대길이


for i in range(1, n):
    for j in range(0, i):
        if array[j] < array[i]:
            dp[i] = max(dp[i], dp[j] + 1)

print(max(dp))