# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/
# https://www.youtube.com/watch?v=iUSXEvV2IUA&feature=youtu.be&ab_channel=BrainRefactor
# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/discuss/152682/Python-simple-recursive-solution-with-detailed-explanation

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        if root == p or root == q:
            return root
        
        left, right = None, None
        
        if root.left:
            left = self.lowestCommonAncestor(root.left, p, q)
        if root.right:
            right = self.lowestCommonAncestor(root.right, p, q)
            
        if left and right:
            return root
        else:
            return left or right
        