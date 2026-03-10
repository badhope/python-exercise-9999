# -----------------------------
# 题目：字符串基本操作。
# 描述：创建字符串 "Python Programming"，计算其长度，转换为大写，替换"Python"为"Java"。
# -----------------------------

def main():
    s = "Python Programming"
    
    print(f"原字符串: {s}")
    print(f"长度: {len(s)}")
    print(f"大写: {s.upper()}")
    print(f"替换后: {s.replace('Python', 'Java')}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# len()：返回字符串长度（字符数）
# upper()：返回字符串的大写版本
# replace(old, new)：替换字符串中的子串