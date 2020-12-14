# https://leetcode.com/problems/minimum-depth-of-binary-tree/
# https://leetcode.com/problems/minimum-depth-of-binary-tree/discuss/36239/Python-BFS-and-DFS-solutions

from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minDepth(self, root: TreeNode) -> int:
        if root is None:
            return 0
        
        q = deque([])
        q.append((root, 1))
        while q:
            node, depth = q.popleft()
            if node:
                if not node.left and not node.right:
                    return depth
                else:
                    q.append((node.left, depth + 1))
                    q.append((node.right, depth + 1))
        