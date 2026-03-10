# -----------------------------
# 题目：字母移位。
# 描述：将字母循环后移n位。
# -----------------------------

def caesar_cipher(s, shift):
    result = ""
    for c in s:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            result += chr((ord(c) - base + shift) % 26 + base)
        else:
            result += c
    return result

def main():
    print(f"ABC移位1: {caesar_cipher('ABC', 1)}")


if __name__ == "__main__":
    main()
