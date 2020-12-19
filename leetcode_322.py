# https://leetcode.com/problems/coin-change/
# https://www.youtube.com/watch?v=1R0_7HqNaW0&ab_channel=KevinNaughtonJr.

class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        dp = [amount + 1] * (amount + 1)
        dp[0] = 0
        
        for i in range(amount+1):
            for coin in coins:
                if coin <= i:
                    dp[i] = min(dp[i], 1 + dp[i - coin])
        
        if dp[amount] == amount + 1:
            return -1
        
        return dp[amount]
        