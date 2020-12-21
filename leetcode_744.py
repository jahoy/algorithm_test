# https://leetcode.com/problems/find-smallest-letter-greater-than-target/
# https://leetcode.com/problems/find-smallest-letter-greater-than-target/discuss/757403/Python-O(N)-and-O(Log-N)-solutions-with-explanation


class Solution:
    def nextGreatestLetter(self, letters: List[str], target: str) -> str:
        if target < letters[0] or target >= letters[-1]: return letters[0]
        
        l, r = 0, len(letters) - 1
        
        while l < r:
            mid = (l + r ) // 2
            
            if target < letters[mid]:
                r = mid
            elif target >= letters[mid]:
                l = mid + 1
        return letters[r]
        