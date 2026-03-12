# -----------------------------
# 题目：简易登录系统。
# 描述：实现用户登录验证，支持用户名密码验证。
# -----------------------------

users = {
    "admin": "123456",
    "user1": "password",
    "guest": "guest"
}

def login(username, password):
    if username in users and users[username] == password:
        return True, f"欢迎, {username}!"
    return False, "用户名或密码错误"

def main():
    result, message = login("admin", "123456")
    print(message)
    result, message = login("admin", "wrong")
    print(message)


if __name__ == "__main__":
    main()
