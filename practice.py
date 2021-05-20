
class Solution:
    def productExceptSelf(self, nums):
        """[summary]

        Args:
            nums (LIST[int])
        Output:
            List[int]
        """

        output = [1] * len(nums)
        lprod = 1
        rprod = 1

        for i in range(len(nums)):
            output[i] *= lprod
            lprod *= nums[i]
            
            output[~i] *= rprod
            rprod *= nums[~i]
        
        return output