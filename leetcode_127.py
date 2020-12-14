# https://leetcode.com/problems/word-ladder/
# https://leetcode.com/problems/word-ladder/discuss/157376/Python-(BFS)-tm

from collections import deque
import string

class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        arr = set(wordList)
        alphabet = string.ascii_lowercase
        q = deque([])
        visited = set()
        q.append((beginWord, 1))
        visited.add(beginWord)
        while q:
            word, length = q.popleft()
            if word == endWord:
                return length
            
            for i in range(len(word)):
                for ch in alphabet:
                    new_word = word[:i] + ch + word[i+1:]
                    if new_word in arr and new_word not in visited:
                        q.append((new_word, length+1))
                        visited.add(new_word)

        return 0
        
        