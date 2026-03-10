# -----------------------------
# 题目：列表元素操作。
# 描述：对列表 [1,2,3,4,5] 进行插入、删除、反转操作。
# -----------------------------

def main():
    lst = [1, 2, 3, 4, 5]
    print(f"原列表: {lst}")
    
    lst.insert(2, 99)
    print(f"插入后: {lst}")
    
    lst.remove(3)
    print(f"删除后: {lst}")
    
    lst.reverse()
    print(f"反转后: {lst}")
    
    lst.pop()
    print(f"pop后: {lst}")


if __name__ == "__main__":
    main()
