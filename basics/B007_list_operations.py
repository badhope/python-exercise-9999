# -----------------------------
# 题目：列表基本操作。
# 描述：创建列表 fruits = ["apple", "banana", "cherry"]，添加"orange"，删除"banana"，排序后输出。
# -----------------------------

def main():
    fruits = ["apple", "banana", "cherry"]
    
    fruits.append("orange")
    fruits.remove("banana")
    fruits.sort()
    
    print(f"列表操作后: {fruits}")
    print(f"第一个元素: {fruits[0]}")
    print(f"列表长度: {len(fruits)}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# append()：在列表末尾添加元素
# remove()：删除第一个匹配的元素
# sort()：原地排序（改变原列表）
# len()：返回列表元素个数