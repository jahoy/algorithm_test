# https://leetcode.com/problems/decode-ways/
# https://leetcode.com/problems/decode-ways/discuss/253018/Python%3A-Easy-to-understand-explanation-bottom-up-dynamic-programming



class Solution:
    def numDecodings(self, s: str) -> int:
        dp = [0] * (len(s)+1)

        # base case initialization
        dp[0] = 1 
        dp[1] = 0 if s[0] == "0" else 1
         
        for i in range(2, len(s) + 1): 
            # One step jump
            if int(s[i-1]) != 0 :   
                dp[i] += dp[i - 1]
            # Two step jump
            if  10 <= int(s[i-2:i]) <= 26: 
                dp[i] += dp[i - 2]
        return dp[-1]