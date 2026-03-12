# -----------------------------
# 题目：实现密码生成器。
# 描述：生成指定长度和复杂度的随机密码。
# -----------------------------

import random
import string

class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def generate(self, length=12, use_upper=True, use_digits=True, use_special=True):
        chars = self.lowercase
        required = [random.choice(self.lowercase)]
        
        if use_upper:
            chars += self.uppercase
            required.append(random.choice(self.uppercase))
        
        if use_digits:
            chars += self.digits
            required.append(random.choice(self.digits))
        
        if use_special:
            chars += self.special
            required.append(random.choice(self.special))
        
        remaining_length = length - len(required)
        password = required + [random.choice(chars) for _ in range(remaining_length)]
        
        random.shuffle(password)
        return ''.join(password)
    
    def generate_multiple(self, count, **kwargs):
        return [self.generate(**kwargs) for _ in range(count)]
    
    def check_strength(self, password):
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in self.special for c in password):
            score += 1
        
        if score <= 2:
            return "弱"
        elif score <= 4:
            return "中等"
        else:
            return "强"

def main():
    generator = PasswordGenerator()
    
    print("生成密码:")
    for i in range(3):
        password = generator.generate(length=16)
        strength = generator.check_strength(password)
        print(f"  {password} (强度: {strength})")


if __name__ == "__main__":
    main()
