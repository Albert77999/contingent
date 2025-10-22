# Contingent 项目学习笔记 - 02：装饰器深度理解

## 装饰器七问 - 标准答案

### Q1: 装饰器是在什么时候执行的？

**答案**：在函数定义时执行，而不是函数调用时

```python
@my_decorator  # ← 这一刻装饰器就执行了
def hello():
    print("Hello!")
```

**C++ 对比**：类似于全局对象的构造函数在 main 之前执行

### Q2: `@decorator` 等价于什么？

**答案**：`func = decorator(func)`

```python
# 这两种写法完全等价：
@my_decorator
def hello():
    pass

# 等价于：
def hello():
    pass
hello = my_decorator(hello)
```

### Q3: 为什么需要 `@wraps`？

**答案**：保留原函数的元数据（名称、文档、签名等）

```python
from functools import wraps

def good_decorator(func):
    @wraps(func)  # ← 关键！
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

没有 `@wraps` 的问题：
- ❌ 函数名变成 'wrapper'
- ❌ 文档字符串丢失
- ❌ 调试困难

### Q4: 类方法装饰器如何访问实例变量？

**答案**：通过闭包捕获 `self`

```python
class MyClass:
    def __init__(self):
        self.cache = {}
    
    def my_decorator(self, func):
        def wrapper(*args):
            # wrapper 可以访问 self.cache
            key = (func.__name__, args)
            if key in self.cache:
                return self.cache[key]
            result = func(*args)
            self.cache[key] = result
            return result
        return wrapper
```

**Contingent 的应用**：
```python
class Project:
    def task(self, task_function):  # self 在这里
        def wrapper(*args):
            # 可以访问 self._cache, self._graph 等
            pass
        return wrapper
```

### Q5: 三层装饰器（带参数）如何工作？

**答案**：装饰器工厂 → 装饰器 → 包装函数

```python
def repeat(times):           # 第1层：装饰器工厂
    def decorator(func):     # 第2层：真正的装饰器
        def wrapper(*args):  # 第3层：包装函数
            for _ in range(times):
                func(*args)
        return wrapper
    return decorator

@repeat(3)  # 先调用 repeat(3) 返回 decorator
def hello():  # 然后用 decorator 装饰 hello
    print("Hello")
```

### Q6: 如何用装饰器实现缓存？

**答案**：在装饰器中维护一个字典

```python
def memoize(func):
    cache = {}  # 闭包中的缓存
    
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    return wrapper
```

**Contingent 的实现**：
```python
class Project:
    def __init__(self):
        self._cache = {}
    
    def task(self, func):
        def wrapper(*args):
            task = Task(wrapper, args)
            if task in self._cache:
                return self._cache[task]
            result = func(*args)
            self._cache[task] = result
            return result
        return wrapper
```

### Q7: 如何用装饰器追踪调用关系？

**答案**：维护一个调用栈

```python
class CallTracker:
    def __init__(self):
        self.call_stack = []
        self.dependencies = {}
    
    def track(self, func):
        def wrapper(*args):
            task_id = (func.__name__, args)
            
            # 记录依赖关系
            if self.call_stack:
                parent = self.call_stack[-1]
                self.dependencies[parent].append(task_id)
            
            # 压栈
            self.call_stack.append(task_id)
            try:
                result = func(*args)
            finally:
                self.call_stack.pop()
            
            return result
        return wrapper
```

## 装饰器练习成果

### 已完成的练习
1. ✅ 最简单的装饰器
2. ✅ 带参数的装饰器
3. ✅ 保留函数元数据
4. ✅ 类方法装饰器
5. ✅ 带参数的装饰器（三层）
6. ✅ 模拟 Contingent 的装饰器

### 自己实现的 SimpleProject

```python
class SimpleProject:
    def __init__(self):
        self.cache = {}
        self.call_stack = []
        self.dependencies = {}
    
    def task(self, func):
        def wrapper(*args):
            task_id = (func.__name__, args)
            
            # 缓存检查
            if task_id in self.cache:
                return self.cache[task_id]
            
            # 依赖记录
            if self.call_stack:
                parent_task = self.call_stack[-1]
                if parent_task not in self.dependencies:
                    self.dependencies[parent_task] = []
                self.dependencies[parent_task].append(task_id)
            
            # 执行
            self.call_stack.append(task_id)
            try:
                result = func(*args)
            finally:
                self.call_stack.pop()
            
            self.cache[task_id] = result
            return result
        
        return wrapper
```

## 关键理解点

1. **闭包的力量**：内层函数可以访问和修改外层变量
2. **装饰器的时机**：定义时 vs 调用时
3. **@wraps 的重要性**：保留元数据，便于调试
4. **类方法装饰器**：通过 self 共享状态
5. **依赖追踪**：调用栈 + 图结构

## C++ 对比理解

```cpp
// 类似的三层 lambda 嵌套
auto repeat(int times) {
    return [times](auto func) {
        return [times, func](auto... args) {
            for (int i = 0; i < times; i++) {
                func(args...);
            }
        };
    };
}
```

## 学习收获

- ✅ 理解了装饰器的本质
- ✅ 能够实现自己的装饰器系统
- ✅ 理解了 Contingent 的 @task 装饰器如何工作
- ✅ 掌握了闭包和作用域

