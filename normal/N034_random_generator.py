# -----------------------------
# 题目：实现简单的随机数生成器。
# 描述：支持各种随机数和随机选择功能。
# -----------------------------

import random
import string

class RandomGenerator:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
    
    def integer(self, min_val, max_val):
        return random.randint(min_val, max_val)
    
    def float_num(self, min_val=0, max_val=1):
        return random.uniform(min_val, max_val)
    
    def boolean(self, probability=0.5):
        return random.random() < probability
    
    def choice(self, sequence):
        if not sequence:
            return None
        return random.choice(sequence)
    
    def sample(self, sequence, k):
        if k > len(sequence):
            k = len(sequence)
        return random.sample(sequence, k)
    
    def shuffle(self, sequence):
        result = list(sequence)
        random.shuffle(result)
        return result
    
    def string(self, length, chars=None):
        if chars is None:
            chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def password(self, length=12):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return self.string(length, chars)
    
    def color(self):
        r = self.integer(0, 255)
        g = self.integer(0, 255)
        b = self.integer(0, 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def date(self, start_year=2000, end_year=2024):
        year = self.integer(start_year, end_year)
        month = self.integer(1, 12)
        day = self.integer(1, 28)
        return f"{year}-{month:02d}-{day:02d}"
    
    def name(self):
        first_names = ['张', '李', '王', '刘', '陈', '杨', '黄', '赵', '周', '吴']
        last_names = ['伟', '芳', '娜', '敏', '静', '丽', '强', '磊', '军', '洋']
        return self.choice(first_names) + self.choice(last_names)
    
    def email(self):
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'qq.com', '163.com']
        username = self.string(8, string.ascii_lowercase)
        return f"{username}@{self.choice(domains)}"
    
    def phone(self):
        prefixes = ['138', '139', '150', '151', '186', '187', '188']
        return self.choice(prefixes) + ''.join([str(self.integer(0, 9)) for _ in range(8)])
    
    def uuid(self):
        return ''.join([
            self.string(8, string.hexdigits.lower()),
            self.string(4, string.hexdigits.lower()),
            self.string(4, string.hexdigits.lower()),
            self.string(4, string.hexdigits.lower()),
            self.string(12, string.hexdigits.lower())
        ])

def main():
    gen = RandomGenerator()
    
    print("随机数生成:")
    print(f"  整数(1-100): {gen.integer(1, 100)}")
    print(f"  浮点数: {gen.float_num():.4f}")
    print(f"  布尔值: {gen.boolean()}")
    print(f"  字符串: {gen.string(10)}")
    print(f"  密码: {gen.password()}")
    print(f"  颜色: {gen.color()}")
    print(f"  日期: {gen.date()}")
    print(f"  姓名: {gen.name()}")
    print(f"  邮箱: {gen.email()}")
    print(f"  电话: {gen.phone()}")


if __name__ == "__main__":
    main()
