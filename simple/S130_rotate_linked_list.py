# -----------------------------
# 题目：旋转链表。
# 描述：将链表向右旋转k个位置。
# -----------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def rotate_right(head, k):
    if not head:
        return head
    length = 1
    tail = head
    while tail.next:
        tail = tail.next
        length += 1
    k = k % length
    if k == 0:
        return head
    tail.next = head
    steps = length - k
    current = head
    for _ in range(steps - 1):
        current = current.next
    new_head = current.next
    current.next = None
    return new_head

def main():
    print("旋转链表演示")


if __name__ == "__main__":
    main()
