# https://leetcode.com/problems/binary-tree-level-order-traversal/
# https://www.youtube.com/watch?v=XZnWETlZZ14&ab_channel=KevinNaughtonJr.

from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def levelOrder(self, root: TreeNode) -> List[List[int]]:
        result = []
        if root is None:
            return result
        q = deque([])
        q.append(root)
        while q:
            size = len(q)
            current_level_list = []
            for i in range(size):
                current_node = q.popleft()
                current_level_list.append(current_node.val)
                if current_node.left:
                    q.append(current_node.left)
                if current_node.right:
                    q.append(current_node.right)
            result.append(current_level_list)
        return result