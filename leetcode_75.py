# https://leetcode.com/problems/sort-colors/
# https://leetcode.com/problems/sort-colors/discuss/681526/Python-O(n)-3-pointers-in-place-approach-explained


class Solution:
    def sortColors(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        beg, med, end = 0, 0, len(nums) - 1
        
        while med <= end:
            if nums[med] == 0:
                nums[beg], nums[med] = nums[med], nums[beg]
                beg += 1
                med += 1
            elif nums[med] == 2:
                nums[med], nums[end] = nums[end], nums[med]
                end -= 1
            else:
                med += 1
        return nums
        