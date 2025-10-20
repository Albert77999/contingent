
"""练习3: 使用 @wraps 保留元数据"""

from functools import wraps

# 问题演示
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def good_decorator(func):
    @wraps(func)  # 这行很重要！
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@bad_decorator
def function1():
    """这是 function1 的文档"""
    pass

@good_decorator
def function2():
    """这是 function2 的文档"""
    pass


print("="*60)
print("练习3: 函数元数据")
print("="*60)

print("没有 @wraps:")
print(f"  名称: {function1.__name__}")
print(f"  文档: {function1.__doc__}")

print("\n有 @wraps:")
print(f"  名称: {function2.__name__}")
print(f"  文档: {function2.__doc__}")

print("\n为什么需要 @wraps?")
print("  ✓ 保留原函数的名称")
print("  ✓ 保留原函数的文档字符串")
print("  ✓ 保留其他元数据")
print("\nContingent 就是这样用的！")