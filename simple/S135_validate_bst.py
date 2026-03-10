# -----------------------------
# 题目：验证二叉搜索树。
# 描述：验证二叉树是否为二叉搜索树。
# -----------------------------

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    if not root:
        return True
    if root.val <= min_val or root.val >= max_val:
        return False
    return is_valid_bst(root.left, min_val, root.val) and is_valid_bst(root.right, root.val, max_val)

def main():
    print("验证二叉搜索树演示")


if __name__ == "__main__":
    main()
