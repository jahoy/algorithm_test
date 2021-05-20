class Solution:
    def findDuplicates(self, nums:List[int]) -> List[int]:
        ans = []
        for num in nums:
            value = abs(num)

            if nums[value - 1] < 0:
                ans.append(value)
            else:
                nums[value - 1] *= -1
        
        return ans