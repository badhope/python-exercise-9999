# -----------------------------
# 题目：字符串编码和解码。
# 描述：将字符串进行 base64 编码和解码。
# -----------------------------

import base64

def main():
    s = "Hello Python"
    encoded = base64.b64encode(s.encode()).decode()
    decoded = base64.b64decode(encoded.encode()).decode()
    print(f"原字符串: {s}")
    print(f"编码后: {encoded}")
    print(f"解码后: {decoded}")


if __name__ == "__main__":
    main()
