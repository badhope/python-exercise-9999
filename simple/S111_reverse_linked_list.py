# -----------------------------
# 题目：反转链表。
# 描述：反转单链表。
# -----------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None
    current = head
    while current:
        next_temp = current.next
        current.next = prev
        prev = current
        current = next_temp
    return prev

def main():
    print("链表反转演示")


if __name__ == "__main__":
    main()
