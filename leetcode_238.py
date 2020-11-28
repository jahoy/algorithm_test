# https://leetcode.com/problems/product-of-array-except-self/
# https://leetcode.com/problems/product-of-array-except-self/discuss/489326/Python-Solution-%2B-Thought-Process.-O(1)-space-O(n)-time

class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        output = []
        # store "left products" 
        for n in nums:
            output.append(output[-1] * n if output else n)
        right = None
        i = len(nums) - 1
        while i >= 0:
            right  = right * nums[i+1] if right != None else 1
            output[i] = output[i-1] * right if i-1 >= 0 else right
            i -= 1
        return output