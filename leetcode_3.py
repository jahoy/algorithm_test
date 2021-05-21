# https://leetcode.com/problems/longest-substring-without-repeating-characters/
# https://leetcode.com/problems/longest-substring-without-repeating-characters/discuss/211683/Python-3-Clean-and-Correct

class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        left = 0
        right = 0
        
        n = len(s) 
        memo = set()
        longgest = 0
        while left < n and right < n:
            if s[right] not in memo:
                memo.add(s[right])
                longgest = max(longgest, right - left + 1)
                right +=1
            else:
                memo.remove(s[left])
                left += 1
        
        return longgest
