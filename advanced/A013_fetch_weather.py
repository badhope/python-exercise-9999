# -----------------------------
# 题目：网络天气查询器。
# 描述：使用 requests 库请求模拟天气 API，获取并解析 JSON 数据。
#      打印出城市名称和温度。
#      注意：这里使用一个公开的模拟 API 地址。
#
# 示例：
# 调用 API 返回：{"city": "Beijing", "temp": 25, "weather": "Sunny"}
# 程序输出：城市：Beijing, 温度：25°C, 天气：Sunny
# -----------------------------

# 制作提示：
# 1. 需要先安装库：pip install requests。
# 2. 使用 requests.get(url) 发送请求。
# 3. 使用 response.json() 解析返回的 JSON 数据。
# 4. 这里的 API 是模拟的，实际开发中需要注册真实的 API Key。

# ========== 普通答案 ==========
import requests

def get_weather():
    # 这是一个公开的模拟测试 API，返回简单的 JSON
    url = "https://jsonplaceholder.typicode.com/users/1" 
    
    try:
        response = requests.get(url)
        # 判断状态码是否为 200 (成功)
        if response.status_code == 200:
            data = response.json()
            # 模拟解析天气数据（这里借用用户数据里的 name 和 id 模拟城市和温度）
            print(f"模拟城市: {data['name']}")
            print(f"模拟数据ID: {data['id']}")
        else:
            print("请求失败，请检查网络")
    except Exception as e:
        print(f"发生错误: {e}")

get_weather()

# ========== 运行效果 ==========
# 模拟城市: Leanne Graham
# 模拟数据ID: 1

# ========== 详细解析版 ==========
# 导入 requests 库，它是 Python 爬虫和接口测试的神器
import requests

def get_weather():
    # API 地址，就像你要访问的网页链接
    url = "https://jsonplaceholder.typicode.com/users/1"
    
    try:
        # 发送 GET 请求，就像浏览器输入网址回车
        response = requests.get(url)
        
        # status_code 200 代表服务器说“OK，给你数据”
        if response.status_code == 200:
            # .json() 把服务器返回的字符串自动转成 Python 的字典
            data = response.json()
            
            # 从字典里取值，就像之前学的字典操作
            print(f"模拟城市: {data['name']}")
            print(f"模拟数据ID: {data['id']}")
        else:
            print("请求失败，请检查网络")
            
    except Exception as e:
        # 网络请求容易出错（断网、超时），必须加异常处理
        print(f"发生错误: {e}")

get_weather()

# ========== 大白话解释 ==========
# requests 就是一个送快递的跑腿小哥。
# 你给他一个地址，他跑去服务器那里把数据取回来。
# .json() 就像是把快递盒子拆开，把里面的东西拿出来摆好。
# 有了它，你的 Python 就能和全世界的服务器对话了。

# ========== 扩展语句 ==========
# 扩展：可以找一个真实的免费天气 API（如 OpenWeatherMap），
# 尝试根据用户输入的城市名动态拼接 URL 进行查询。
