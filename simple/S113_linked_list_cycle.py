# -----------------------------
# 题目：环形链表。
# 描述：判断链表是否有环。
# -----------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

def main():
    print("环形链表检测演示")


if __name__ == "__main__":
    main()
