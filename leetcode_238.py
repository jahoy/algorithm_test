# https://leetcode.com/problems/product-of-array-except-self/
# https://leetcode.com/problems/product-of-array-except-self/discuss/239771/Python-solution


class Solution:
    def productExceptSelf(self, nums):
        output = [1] * len(nums)
        lprod = 1
        rprod = 1

        for i in range(len(nums)):
            output[i] *= lprod
            lprod *= nums[i]
            
            output[~i] *= rprod
            rprod *= nums[~i]
        
        return output