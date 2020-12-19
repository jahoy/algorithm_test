# https://leetcode.com/problems/longest-palindromic-substring/
# https://www.youtube.com/watch?v=IrD8MA054vA&ab_channel=TimothyHChang


class Solution:
    def longestPalindrome(self, s: str) -> str:
        def helper(l, r):
            while(l >= 0 and r < len(s) and s[l] == s[r]):
                l -= 1
                r += 1
            return s[l+1:r]
        
        res = ""
        for i in range(len(s)):
            # 홀수
            test = helper(i,i)
            if len(test) > len(res): res = test
            # 짝수
            test = helper(i,i+1)
            if len(test) > len(res): res = test
        
        return res
