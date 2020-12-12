# https://leetcode.com/problems/letter-combinations-of-a-phone-number/


class Solution:
    def letterCombinations(self, digits: str) -> List[str]:
        map_ = {
            '2' : 'abc',
            '3' : 'def',
            '4' : 'ghi',
            '5' : 'jkl',
            '6' : 'mno',
            '7' : 'pqrs',
            '8' : 'tuv',
            '9' : 'wxyz'
        }
        result = []
        
        
        def make_combinations(i, cur):
            if len(cur) == len(digits):
                if len(cur) > 0:
                    result.append(''.join(cur))
                return
            
            for ch in map_[digits[i]]:
                cur.append(ch)
                make_combinations(i+1, cur)
                cur.pop()
        
        make_combinations(0, [])
        return result