# -----------------------------
# 题目：实现异步生成器。
# 描述：使用async for处理异步数据流。
# -----------------------------

import asyncio

async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def async_filter(aiterable, predicate):
    async for item in aiterable:
        if predicate(item):
            yield item

async def async_map(aiterable, func):
    async for item in aiterable:
        yield func(item)

async def async_collect(aiterable):
    result = []
    async for item in aiterable:
        result.append(item)
    return result

async def main():
    print("异步范围:")
    async for i in async_range(5):
        print(i, end=" ")
    print()
    
    print("\n异步管道:")
    numbers = async_range(10)
    evens = async_filter(numbers, lambda x: x % 2 == 0)
    doubled = async_map(evens, lambda x: x * 2)
    result = await async_collect(doubled)
    print(f"结果: {result}")


if __name__ == "__main__":
    asyncio.run(main())
