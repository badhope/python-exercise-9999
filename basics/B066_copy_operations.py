# -----------------------------
# 题目：浅拷贝和深拷贝。
# 描述：演示列表的浅拷贝和深拷贝区别。
# -----------------------------

import copy

def main():
    original = [[1, 2], [3, 4]]
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)
    
    shallow[0][0] = 99
    print(f"原列表: {original}")
    print(f"浅拷贝后修改: {shallow}")
    print(f"深拷贝: {deep}")


if __name__ == "__main__":
    main()
