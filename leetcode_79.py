# https://leetcode.com/problems/word-search/
# https://www.youtube.com/watch?v=RqffW0smIbQ&ab_channel=TimothyHChang

class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        n, m = len(board[0]), len(board)      
        
        def helper(r, c, pos):
            if pos >= len(word):
                return True
            
            elif 0 <= r < m and 0 <= c < n and board[r][c] == word[pos]:
                temp = board[r][c]
                board[r][c] = None
                if helper(r+1, c , pos+1) or helper(r-1, c , pos+1) or helper(r, c-1 , pos+1) or helper(r, c+1 , pos+1):
                    return True
                board[r][c] = temp
            return False
        
        for i in range(0, m):
            for j in range(0, n):
                if helper(i, j, 0):
                    return True
        return False
        