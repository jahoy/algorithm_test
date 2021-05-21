class Solution:
    def moveZeros(self, nums:List[int]) -> None:
        slow = 0
        for fast in range(len(nums)):
            if nums[fast] != 0 and nums[slow] == 0:
                nums[fast], nums[slow] = nums[slow], nums[fast]
            
            if nums[slow] != 0:
                slow += 1
        
        return nums