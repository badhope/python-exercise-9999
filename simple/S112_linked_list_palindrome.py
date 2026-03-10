# -----------------------------
# 题目：回文链表。
# 描述：判断链表是否为回文。
# -----------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def is_palindrome_linked_list(head):
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    return vals == vals[::-1]

def main():
    print("回文链表演示")


if __name__ == "__main__":
    main()
