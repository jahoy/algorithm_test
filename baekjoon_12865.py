# https://www.acmicpc.net/problem/12865

n, k = map(int, input().split())
dp = [[0] * (k + 1) for _ in range(n + 1)] 
# dp[i][j] = 배낭에 넣은 물품의 무게 합이 j일 때 얻을 수 있는 최대 가치


for i in range(1, n + 1):
    w, v = map(int, input().split())
    for j in range(1, k + 1):
        if j < w:
            dp[i][j] = dp[i - 1][j]
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - w] + v)  # 미포함 vs 포함
            
print(dp[n][k])
