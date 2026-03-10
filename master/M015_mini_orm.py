# -----------------------------
# 题目：简易 ORM (对象关系映射) 引擎。
# 描述：不使用数据库，模拟实现一个类似 Django ORM 或 SQLAlchemy 的微型系统。
#      定义 Model 基类，子类继承后可以直接 save() 和 all()。
#
# 示例：
# class User(Model): pass
# u = User(name="Tom", age=18)
# u.save() -> 存入类变量中
# User.all() -> 返回所有 User 对象
# -----------------------------

# 制作提示：
# 1. 使用类变量 `objects = []` 存储所有实例。
# 2. Model 基类实现 save 方法（将 self 加入 objects）。
# 3. Model 基类实现 all 类方法（返回 objects）。

# ========== 普通答案 ==========
class Model:
    # 类属性，所有实例共享这一个列表
    _database = []

    def __init__(self, **kwargs):
        # 动态设置属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        # 把自己存进数据库
        self._database.append(self)
        print(f"已保存: {self.__dict__}")

    @classmethod
    def all(cls):
        # 返回所有数据
        return cls._database

class User(Model):
    pass

# 使用
u1 = User(name="Tom", age=18)
u1.save()

u2 = User(name="Jerry", age=20)
u2.save()

print("所有用户:", [u.name for u in User.all()])

# ========== 运行效果 ==========
# 已保存: {'name': 'Tom', 'age': 18}
# 已保存: {'name': 'Jerry', 'age': 20}
# 所有用户: ['Tom', 'Jerry']

# ========== 详细解析版 ==========
# 定义基类 Model，相当于数据库的“表结构”模板
class Model:
    # _database 是类变量，相当于一张表，存所有行数据
    # _ 前缀表示这是个内部变量，外部最好别乱动
    _database = []

    # __init__ 接受任意关键字参数 **kwargs
    # 比如传入 name="Tom"，就会变成 self.name = "Tom"
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # setattr 是 setattr(self, 'name', 'Tom') 的动态写法
            setattr(self, key, value)

    # 实例方法：保存
    def save(self):
        # self 就是当前的实例对象，把它 append 到类列表里
        self._database.append(self)
        print(f"已保存: {self.__dict__}")

    # 类方法：查询所有
    # @classmethod 装饰器表示这个方法属于类，不属于某个对象
    # cls 代表类本身
    @classmethod
    def all(cls):
        return cls._database

# User 继承 Model，自动拥有了 save 和 all 的能力
# 不需要自己写存取逻辑了
class User(Model):
    pass

# 测试代码
u1 = User(name="Tom", age=18)
u1.save()

u2 = User(name="Jerry", age=20)
u2.save()

# User.all() 调用的是类方法，拿到所有数据
print("所有用户:", [u.name for u in User.all()])

# ========== 大白话解释 ==========
# 这就像是在造流水线。
# Model 是流水线的母版。
# User 是具体的产品模具。
# save 是把产品打包入库的机械臂。
# all 是仓库管理员，你要多少他给你拿多少。
# 写好这套框架，以后定义别的产品（如 Book, Order），只要继承一下，立马就能存取，不用重复写代码。

# ========== 扩展语句 ==========
# 扩展：实现一个 get(name="Tom") 方法，能够按条件筛选数据，
# 这就是 ORM 最核心的查询功能雏形。
