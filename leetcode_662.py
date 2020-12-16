# https://leetcode.com/problems/maximum-width-of-binary-tree/
# https://leetcode.com/problems/maximum-width-of-binary-tree/discuss/688259/Python-solution-O(N)-BFS-traversal
# https://seong7.github.io/algorithms/2020/07/10/leetcode-662.html


from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def widthOfBinaryTree(self, root: TreeNode) -> int:
        if not root:
            return 0
        
        q = deque([])
        q.append((root, 1))
        
        max_width = 0
        while q:
            _, start_index = q[0]
            for i in range(len(q)):
                node, index = q.popleft()
                if node.left:
                    q.append((node.left, index * 2))
                if node.right:
                    q.append((node.right, index * 2 + 1))
                
            max_width = max(max_width, index - start_index + 1)
        return max_width
                
                
        