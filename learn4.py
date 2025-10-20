# !/usr/bin/env python
"""练习5: 装饰器本身接受参数"""

from functools import wraps

# 这是一个"装饰器工厂"
def repeat(times):
    """返回一个重复执行的装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for i in range(times):
                print(f"  第 {i+1} 次执行")
                result = func(*args, **kwargs)
                results.append(result)
            return results
        return wrapper
    return decorator


# 测试
@repeat(3)  # 注意：这里传入了参数！
def say_hello(name):
    print(f"    Hello, {name}!")
    return "done"

@repeat(2)
def compute(x):
    print(f"    计算 {x} * 2")
    return x * 2


print("="*60)
print("练习5: 带参数的装饰器")
print("="*60)

print("\n重复3次:")
results1 = say_hello("Alice")
print(f"结果: {results1}")

print("\n重复2次:")
results2 = compute(5)
print(f"结果: {results2}")

print("\n理解装饰器的三层结构:")
print("  1. repeat(times) - 装饰器工厂")
print("  2. decorator(func) - 实际的装饰器")
print("  3. wrapper(*args) - 包装函数")