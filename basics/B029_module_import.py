# -----------------------------
# 题目：模块导入和使用。
# 描述：使用标准库模块 math、random、datetime 进行各种操作。
# -----------------------------

import math
import random
from datetime import datetime, timedelta


def main():
    print(f"math.pi = {math.pi}")
    print(f"math.sqrt(16) = {math.sqrt(16)}")
    print(f"math.pow(2, 3) = {math.pow(2, 3)}")
    
    print(f"random.randint(1, 100) = {random.randint(1, 100)}")
    print(f"random.choice(['a', 'b', 'c']) = {random.choice(['a', 'b', 'c'])}")
    print(f"random.shuffle([1,2,3,4,5]) = ", end="")
    lst = [1, 2, 3, 4, 5]
    random.shuffle(lst)
    print(lst)
    
    now = datetime.now()
    print(f"当前时间: {now}")
    print(f"3天后: {now + timedelta(days=3)}")


if __name__ == "__main__":
    main()


# ========== 详细解析 ==========
# import：导入模块的关键字
# from ... import：从模块导入特定内容
# as：给导入的模块起别名