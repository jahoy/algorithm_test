# https://leetcode.com/problems/minimum-size-subarray-sum/
# https://leetcode.com/problems/minimum-size-subarray-sum/discuss/59093/Python-O(n)-and-O(n-log-n)-solution


class Solution:
    def minSubArrayLen(self, s: int, nums: List[int]) -> int:
        left , total = 0, 0
        
        result = float('inf')
        for right, num in enumerate(nums):
            total += nums[right]
            while total >= s and left <= right:
                result = min(result, right - left + 1)
                total -= nums[left]
                left += 1
        
        return result if result <= len(nums) else 0