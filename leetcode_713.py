# https://leetcode.com/problems/subarray-product-less-than-k/
# https://www.youtube.com/watch?v=4775IgUKfww&ab_channel=AnishMalla
# https://leetcode.com/problems/subarray-product-less-than-k/discuss/108846/Python-solution-with-detailed-explanation


class Solution:
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        left = 0
        length = len(nums)
        product = 1
        
        result = 0
        for right in range(length):
            product *= nums[right]
            
            while product >= k and left <= right:
                product = product // nums[left]
                left += 1
            
            result += right - left + 1
        return result