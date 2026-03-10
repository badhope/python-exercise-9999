# -----------------------------
# 题目：学生管理系统 - 类设计。
# 描述：设计一个 Student 类，包含姓名、学号、分数三个属性。
#      包含一个方法 `print_info()` 打印信息。
#      包含一个方法 `is_pass()` 判断是否及格（60分及格）。
#
# 示例：
# 创建对象：s = Student("张三", "2021001", 85)
# 调用方法：s.print_info() -> 输出：姓名:张三, 学号:2021001, 分数:85
# 调用方法：s.is_pass() -> 输出：恭喜及格
# -----------------------------

# 制作提示：
# 1. 使用 `class` 关键字定义类。
# 2. `__init__` 方法用于初始化属性。
# 3. `self` 代表对象自己。

# ========== 普通答案 ==========
class Student:
    def __init__(self, name, id, score):
        self.name = name
        self.id = id
        self.score = score

    def print_info(self):
        print(f"姓名:{self.name}, 学号:{self.id}, 分数:{self.score}")

    def is_pass(self):
        if self.score >= 60:
            print("恭喜及格")
        else:
            print("不及格，准备补考")

# 实例化对象
s1 = Student("张三", "2021001", 85)
s1.print_info()
s1.is_pass()

s2 = Student("李四", "2021002", 55)
s2.print_info()
s2.is_pass()

# ========== 运行效果 ==========
# 姓名:张三, 学号:2021001, 分数:85
# 恭喜及格
# 姓名:李四, 学号:2021002, 分数:55
# 不及格，准备补考

# ========== 详细解析版 ==========
# 定义一个类，相当于画图纸
class Student:
    # __init__ 是初始化方法（构造函数），造房子打地基用的
    # self 必须有，它代表“我自己”
    def __init__(self, name, id, score):
        # 把传进来的 name 贴到对象身上，变成对象的属性
        self.name = name
        self.id = id
        self.score = score

    # 定义一个行为（方法），打印自己的信息
    def print_info(self):
        # 用 self.name 拿到自己的名字
        print(f"姓名:{self.name}, 学号:{self.id}, 分数:{self.score}")

    # 定义另一个行为，判断及格
    def is_pass(self):
        # 拿自己的分数去比较
        if self.score >= 60:
            print("恭喜及格")
        else:
            print("不及格，准备补考")

# 根据图纸造第一个实实在在的“对象”
s1 = Student("张三", "2021001", 85)
# 让这个对象执行打印动作
s1.print_info()
# 让这个对象执行判断动作
s1.is_pass()

s2 = Student("李四", "2021002", 55)
s2.print_info()
s2.is_pass()

# ========== 大白话解释 ==========
# 类 就像是“月饼模具”。
# __init__ 方法就是做月饼的过程，你往里面塞面粉和数据，一压，一个月饼就出来了。
# self 就是每个月饼自己，张三这个月饼有自己的馅（属性），李四那个有自己的馅。
# 方法 就像是月饼自带的功能，比如“加热”或“看保质期”。

# ========== 扩展语句 ==========
# 扩展：增加一个类属性 `count`，每创建一个学生，count 就 +1，
# 用来统计总共创建了多少学生。
