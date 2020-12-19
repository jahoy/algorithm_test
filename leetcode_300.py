# https://leetcode.com/problems/longest-increasing-subsequence/
# https://leetcode.com/problems/longest-increasing-subsequence/discuss/300914/Python-DP-Easy
# https://www.youtube.com/watch?v=td8JCnqt-JI&t=10s&ab_channel=TimothyHChang


class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        N = len(nums)
        dp = [1] * N
        
        for i in range(N):
            for j in range(i):
                if nums[i] > nums[j]:
                    dp[i] = max(dp[i], dp[j] + 1)
        
        return max(dp)
        