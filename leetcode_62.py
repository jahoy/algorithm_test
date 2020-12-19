# https://leetcode.com/problems/unique-paths/
# https://www.youtube.com/watch?v=6qMFjFC9YSc&ab_channel=KevinNaughtonJr.



class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        dp = [[1] * n for i in range(m)]        # DP Matrix of size m*n intialized to 1

        for r in range(1, m):
            for c in range(1, n):
                dp[r][c] = dp[r - 1][c] + dp[r][c - 1]

        return dp[-1][-1]
 