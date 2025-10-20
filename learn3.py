# !/usr/bin/env python
"""练习4: 理解类方法装饰器（像 Project.task）"""

from functools import wraps

class SimpleCache:
    """简化的缓存类（类似 Project）"""
    
    def __init__(self):
        self.cache = {}
        self.call_count = {}
    
    def cached(self, func):
        """装饰器方法（类似 Project.task）"""
        @wraps(func)
        def wrapper(*args):
            # 创建缓存键
            key = (func.__name__, args)
            
            # 记录调用次数
            if key not in self.call_count:
                self.call_count[key] = 0
            self.call_count[key] += 1
            
            # 检查缓存
            if key in self.cache:
                print(f"  ⚡ 缓存命中: {func.__name__}{args}")
                return self.cache[key]
            
            # 执行并缓存
            print(f"  🔨 执行: {func.__name__}{args}")
            result = func(*args)
            self.cache[key] = result
            return result
        
        return wrapper
    
    def stats(self):
        """显示统计信息"""
        print("\n缓存统计:")
        for key, count in self.call_count.items():
            cached = "是" if key in self.cache else "否"
            print(f"  {key[0]}{key[1]}: 调用{count}次, 已缓存:{cached}")


# 测试
print("="*60)
print("练习4: 类方法装饰器")
print("="*60)

cache = SimpleCache()

@cache.cached  # 注意：这是实例方法！
def expensive_compute(n):
    return n * n

@cache.cached
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("\n测试1: 简单函数")
print(f"结果1: {expensive_compute(5)}")
print(f"结果2: {expensive_compute(5)}")  # 使用缓存

print("\n测试2: 递归函数")
print(f"Fibonacci(5) = {fibonacci(5)}")

cache.stats()

print("\n关键理解:")
print("  ✓ 装饰器可以是类的方法")
print("  ✓ 可以访问 self（实例变量）")
print("  ✓ 这就是 Project.task 的工作方式！")