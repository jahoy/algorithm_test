# https://leetcode.com/problems/maximum-subarray/
# https://www.youtube.com/watch?v=58yMrWfUS7k&ab_channel=thecodingworld


class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        total_sum = max_sum = nums[0]
        
        for num in nums[1:]:
            total_sum = max(total_sum + num, num)
            max_sum = max(max_sum, total_sum)
        return max_sum