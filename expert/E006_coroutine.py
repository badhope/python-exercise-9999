# -----------------------------
# 题目：实现协程。
# 描述：使用yield实现协程通信。
# -----------------------------

def coroutine(func):
    def wrapper(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return wrapper

@coroutine
def grep(pattern):
    print(f"查找: {pattern}")
    while True:
        line = yield
        if pattern in line:
            print(f"匹配: {line}")

@coroutine
def broadcast(targets):
    while True:
        message = yield
        for target in targets:
            target.send(message)

def pipeline(source, *transformers):
    result = source
    for transformer in transformers:
        transformer.send(result)
        result = transformer
    return result

def main():
    g = grep("Python")
    g.send("Hello World")
    g.send("Python is great")
    g.send("Goodbye")
    
    print("\n广播演示:")
    greeter1 = grep("Hello")
    greeter2 = grep("World")
    broadcaster = broadcast([greeter1, greeter2])
    broadcaster.send("Hello there")
    broadcaster.send("World peace")


if __name__ == "__main__":
    main()
