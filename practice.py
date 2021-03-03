# https://leetcode.com/problems/binary-tree-right-side-view/
# https://www.youtube.com/watch?v=uHNb6lwuNyE&ab_channel=TheCodingManual


from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        if not root:
            return []
        
        q = deque([])
        q.append(root)
        
        result = []
        while q:
            current_level_list = []
            for i in range(len(q)):
                node = q.popleft()
                current_level_list.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            result.append(current_level_list[-1])
        return result
                    
                    
                    