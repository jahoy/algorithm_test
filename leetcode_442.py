# https://leetcode.com/problems/find-all-duplicates-in-an-array/
# https://leetcode.com/problems/find-all-duplicates-in-an-array/discuss/776388/Python-O(n)O(1)-solution-how-to-actually-ARRIVE-at-the-solution-(for-beginners)


class Solution:
    def findDuplicates(self, nums: List[int]) -> List[int]:
        ans = []
        for num in nums:
            value = abs(num)
            
            if nums[value - 1] < 0:
                ans.append(value)
            else:
                nums[value - 1] *= -1
                
        return ans