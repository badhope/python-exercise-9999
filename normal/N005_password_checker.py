# -----------------------------
# 题目：密码强度检测。
# 描述：检测密码强度，返回强度等级。
# -----------------------------

def check_password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=" for c in password):
        score += 1
    
    if score <= 2:
        return "弱"
    elif score <= 4:
        return "中"
    else:
        return "强"

def main():
    passwords = ["123456", "password123", "Password123!", "MyStr0ng@Pass"]
    for pwd in passwords:
        print(f"'{pwd}': {check_password_strength(pwd)}")


if __name__ == "__main__":
    main()
