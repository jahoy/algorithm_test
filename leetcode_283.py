# https://leetcode.com/problems/move-zeroes/
# https://leetcode.com/problems/move-zeroes/discuss/562911/Two-pointers-technique-(Python-O(n)-time-O(1)-space

class Solution:
    def moveZeroes(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        slow = 0
        for fast in range(len(nums)):
            if nums[fast] != 0 and nums[slow] == 0:
                nums[fast], nums[slow] = nums[slow], nums[fast]
            
            if nums[slow] != 0:
                slow += 1
        return nums