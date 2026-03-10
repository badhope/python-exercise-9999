# -----------------------------
# 题目：移除链表元素。
# 描述：删除链表中所有值为val的节点。
# -----------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_elements(head, val):
    dummy = ListNode(0)
    dummy.next = head
    current = dummy
    while current.next:
        if current.next.val == val:
            current.next = current.next.next
        else:
            current = current.next
    return dummy.next

def main():
    print("链表操作演示")


if __name__ == "__main__":
    main()
