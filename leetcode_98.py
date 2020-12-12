# https://leetcode.com/problems/validate-binary-search-tree/
# https://www.youtube.com/watch?v=ofuXorE-JKE&feature=youtu.be&ab_channel=SuboptimalEngineer

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isValidBST(self, root: TreeNode) -> bool:
        return self.helper(root, float('-inf'), float('inf'))
    
    def helper(self, root, min_value, max_value):
        if root is None:
            return True
        if root.val <= min_value or root.val >= max_value:
            return False
        
        left_tree = self.helper(root.left, min_value, root.val)
        right_tree = self.helper(root.right, root.val, max_value)
        
        return left_tree and right_tree
        