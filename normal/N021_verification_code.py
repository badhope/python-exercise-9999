# -----------------------------
# 题目：验证码生成器。
# 描述：生成指定长度的随机验证码。
# -----------------------------

import random
import string

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def main():
    print(f"验证码: {generate_verification_code(6)}")


if __name__ == "__main__":
    main()
