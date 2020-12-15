# https://leetcode.com/problems/path-sum/
# https://www.youtube.com/watch?v=IIPJ9tRYsg0&ab_channel=SuboptimalEngineer

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def hasPathSum(self, root: TreeNode, sum: int) -> bool:
        if root is None:
            return False
        
        target = sum - root.val
        
        if root.right == None and root.left == None and target == 0:
            return True
        
        return self.hasPathSum(root.left, target) or self.hasPathSum(root.right, target)