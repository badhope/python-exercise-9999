# -----------------------------
# 题目：健壮的除法计算模块。
# 描述：编写一个安全的除法函数，必须处理以下异常情况：
#      1. 除数为 0 (ZeroDivisionError)
#      2. 输入的不是数字
#      3. 用户强行中断程序
#      无论发生什么，程序都不能崩，而是给出友好提示。
#
# 示例：
# 输入：10, 0 -> 输出：数学错误：除数不能为零
# 输入：a, 2 -> 输出：类型错误：请输入数字
# -----------------------------

# 制作提示：
# 1. 使用 try...except...finally 结构。
# 2. 捕获特定的异常类型。
# 3. 使用 raise 可以主动抛出异常（可选）。

# ========== 普通答案 ==========
def safe_divide():
    try:
        # 获取输入
        num1_str = input("请输入被除数：")
        num2_str = input("请输入除数：")
        
        # 尝试转换并计算
        result = float(num1_str) / float(num2_str)
        print(f"结果是: {result}")
        
    except ZeroDivisionError:
        print("数学错误：除数不能为零！")
    except ValueError:
        print("类型错误：请输入有效的数字，别乱打字！")
    except KeyboardInterrupt:
        print("\n检测到中断，程序已退出。")
    except Exception as e:
        # 兜底，捕获其他未知错误
        print(f"发生未知错误: {e}")

# 调用
safe_divide()

# ========== 运行效果 ==========
# 请输入被除数：100
# 请输入除数：0
# 数学错误：除数不能为零！

# ========== 详细解析版 ==========
def safe_divide():
    # try 块里面放可能会出错的代码
    # 程序会试着运行这里，如果出错了，马上跳到 except
    try:
        num1_str = input("请输入被除数：")
        num2_str = input("请输入除数：")
        
        # 这一步如果输入了 "abc"，float() 转换失败，会触发 ValueError
        # 如果 num2 是 0，除法运算会触发 ZeroDivisionError
        result = float(num1_str) / float(num2_str)
        print(f"结果是: {result}")
        
    # 专门抓捕“除零错误”
    except ZeroDivisionError:
        print("数学错误：除数不能为零！")
    
    # 专门抓捕“值错误”（比如字符串转数字失败）
    except ValueError:
        print("类型错误：请输入有效的数字，别乱打字！")
        
    # 抓捕用户按 Ctrl+C 强行退出的情况
    except KeyboardInterrupt:
        print("\n检测到中断，程序已退出。")
        
    # 抓捕其他所有漏网之鱼
    # Exception 是所有错误的父类
    except Exception as e:
        print(f"发生未知错误: {e}")

safe_divide()

# ========== 大白话解释 ==========
# try-except 就像是走钢丝底下铺的安全网。
# 正常走钢丝没问题，万一掉下来，不同的 except 就是不同的垫子。
# 如果是摔倒了，去“骨折科”；
# 如果是吓晕了，去“急诊科”。
# 不管发生什么，都不会直接摔在地上（程序崩溃）。

# ========== 扩展语句 ==========
# 扩展：可以添加 finally 代码块，里面的代码无论出错还是不出错，
# 最后都会执行（比如用来关闭文件或数据库连接）。
