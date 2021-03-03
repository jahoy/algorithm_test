# https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/

class Solution:
    def findDisappearedNumbers(self, nums: List[int]) -> List[int]:
        numbers = set()
        missing_nums = []
        for num in nums:
            numbers.add(num)
        
        for i in range(1, len(nums) + 1):
            if i not in numbers:
                missing_nums.append(i)
        
        return missing_nums