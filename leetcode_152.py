# https://leetcode.com/problems/maximum-product-subarray/
# https://www.youtube.com/watch?v=q3Q-2a8NnCQ&ab_channel=TimothyHChang


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        largest_product = most_pos_product = most_neg_product = nums[0]
        
        for i in range(1, len(nums)):
            x = max(nums[i], most_pos_product * nums[i], most_neg_product * nums[i])
            y = min(nums[i], most_pos_product * nums[i], most_neg_product * nums[i])
            
            most_pos_product, most_neg_product = x, y
            largest_product= max(largest_product, most_pos_product)
        return largest_product