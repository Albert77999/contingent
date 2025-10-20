
"""练习7: 添加调试信息，深入理解执行流程"""

from functools import wraps

def debug_decorator(func):
    """带详细调试信息的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n{'='*60}")
        print(f"装饰器调试信息:")
        print(f"{'='*60}")
        print(f"原函数: {func}")
        print(f"原函数名: {func.__name__}")
        print(f"包装函数: {wrapper}")
        print(f"包装函数名: {wrapper.__name__}")  # 因为有 @wraps
        print(f"位置参数: {args}")
        print(f"关键字参数: {kwargs}")
        print(f"即将调用原函数...")
        
        result = func(*args, **kwargs)
        
        print(f"原函数返回: {result}")
        print(f"类型: {type(result)}")
        print(f"返回给调用者: {result}")
        return result
    
    return wrapper


@debug_decorator
def calculate(x, y, operation="+"):
    """执行计算"""
    if operation == "+":
        return x + y
    elif operation == "*":
        return x * y
    return 0


print("练习7: 调试装饰器")

result = calculate(5, 3)
print(f"\n最终在 main 中得到: {result}")

result2 = calculate(5, 3, operation="*")
print(f"\n最终在 main 中得到: {result2}")

print("\n思考:")
print("  1. 装饰器在什么时候被调用？")
print("     → 函数定义时（@decorator 那一刻）")
print("  2. 包装函数在什么时候被调用？")
print("     → 每次调用被装饰的函数时")
print("  3. 原函数还存在吗？")
print("     → 存在，被保存在闭包中")