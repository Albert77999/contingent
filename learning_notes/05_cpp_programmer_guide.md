# Contingent 项目学习笔记 - 05：C++ 程序员专用指南

## Python vs C++ 核心概念对照

### 数据结构映射

| Python | C++ | 说明 |
|--------|-----|------|
| `dict` | `std::unordered_map` | 哈希表 |
| `set` | `std::unordered_set` | 哈希集合 |
| `list` | `std::vector` | 动态数组 |
| `tuple` | `std::tuple` | 元组 |
| `defaultdict(set)` | `std::map<K, std::set<V>>` | 带默认值的映射 |

### Contingent 核心数据结构对照

#### Graph 类

**Python**:
```python
class Graph:
    def __init__(self):
        self._inputs_of = defaultdict(set)
        self._consequences_of = defaultdict(set)
```

**C++ 等价**:
```cpp
class Graph {
private:
    std::unordered_map<Task, std::unordered_set<Task>> inputs_of;
    std::unordered_map<Task, std::unordered_set<Task>> consequences_of;
    
public:
    void add_edge(Task input, Task consequence) {
        consequences_of[input].insert(consequence);
        inputs_of[consequence].insert(input);
    }
};
```

#### Project 类

**Python**:
```python
class Project:
    def __init__(self):
        self._cache = {}
        self._task_stack = []
        self._todo = set()
```

**C++ 等价**:
```cpp
class Project {
private:
    std::unordered_map<Task, Result> cache;
    std::vector<Task> task_stack;
    std::unordered_set<Task> todo;
    Graph graph;
};
```

---

## 装饰器 vs C++ 概念

### 装饰器的 C++ 模拟

**Python**:
```python
@task
def read(filename):
    return open(filename).read()
```

**C++ (Lambda + 模板)**:
```cpp
// 装饰器工厂
template<typename Func>
auto task(Project& project, Func func) {
    return [&project, func](auto... args) {
        Task task_id = Task(func, args...);
        
        // 检查缓存
        if (auto it = project.cache.find(task_id); 
            it != project.cache.end()) {
            return it->second;
        }
        
        // 压栈
        project.task_stack.push_back(task_id);
        
        // 执行
        auto result = func(args...);
        
        // 出栈
        project.task_stack.pop_back();
        
        // 缓存
        project.cache[task_id] = result;
        
        return result;
    };
}

// 使用
auto read = task(project, [](std::string filename) {
    // ...
});
```

### 闭包对比

**Python 闭包**:
```python
def outer():
    x = 10
    def inner():
        return x  # 捕获外层变量
    return inner

f = outer()
print(f())  # 10
```

**C++ Lambda 闭包**:
```cpp
auto outer() {
    int x = 10;
    return [x]() {  // 值捕获
        return x;
    };
}

auto f = outer();
std::cout << f() << std::endl;  // 10
```

**引用捕获对比**:
```python
# Python: 自动引用捕获
def make_counter():
    count = 0
    def increment():
        nonlocal count  # 需要 nonlocal
        count += 1
        return count
    return increment
```

```cpp
// C++: 显式引用捕获
auto make_counter() {
    auto count = std::make_shared<int>(0);
    return [count]() {  // 共享指针捕获
        (*count)++;
        return *count;
    };
}
```

---

## 动态类型 vs 静态类型

### Python 的灵活性

```python
# 同一个字典可以存不同类型
cache = {}
cache[Task1] = "string"
cache[Task2] = 42
cache[Task3] = [1, 2, 3]
cache[Task4] = None
```

### C++ 的解决方案

```cpp
// C++17: std::any
std::unordered_map<Task, std::any> cache;
cache[task1] = std::string("string");
cache[task2] = 42;
cache[task3] = std::vector{1, 2, 3};

// 使用时需要类型转换
auto value = std::any_cast<std::string>(cache[task1]);
```

```cpp
// C++17: std::variant（更好的选择）
using CacheValue = std::variant<std::string, int, std::vector<int>>;
std::unordered_map<Task, CacheValue> cache;

// 使用 std::visit
std::visit([](auto&& value) {
    std::cout << value << std::endl;
}, cache[task]);
```

---

## 哨兵对象模式

### Python 实现

```python
_unavailable = object()  # 唯一的哨兵

if result is _unavailable:  # 身份比较
    # 未找到
```

### C++ 等价实现

```cpp
// 方案1: std::optional (C++17)
std::optional<Result> get_from_cache(Task task) {
    auto it = cache.find(task);
    if (it == cache.end()) {
        return std::nullopt;  // 类似 _unavailable
    }
    return it->second;
}

// 使用
auto result = get_from_cache(task);
if (!result.has_value()) {  // 类似 is _unavailable
    // 未找到
}
```

```cpp
// 方案2: 指针 + nullptr
Result* get_from_cache(Task task) {
    auto it = cache.find(task);
    if (it == cache.end()) {
        return nullptr;  // 类似 _unavailable
    }
    return &it->second;
}

// 使用
if (auto* result = get_from_cache(task); result == nullptr) {
    // 未找到
}
```

---

## namedtuple vs struct

### Python namedtuple

```python
from collections import namedtuple

Task = namedtuple('Task', ('task_function', 'args'))

# 使用
task = Task(wrapper, ('test.txt',))
print(task.task_function)
print(task.args)

# 可哈希，可用作字典键
cache[task] = result
```

### C++ struct

```cpp
struct Task {
    std::function<Result(std::string)> task_function;
    std::tuple<std::string> args;
    
    // 需要手动实现哈希和相等性
    bool operator==(const Task& other) const {
        return task_function.target<void>() == 
               other.task_function.target<void>() &&
               args == other.args;
    }
};

// 哈希函数
namespace std {
    template<>
    struct hash<Task> {
        size_t operator()(const Task& task) const {
            // 组合哈希
            return hash<void*>()(task.task_function.target<void>()) ^
                   hash<std::tuple<std::string>>()(task.args);
        }
    };
}

// 使用
std::unordered_map<Task, Result> cache;
cache[task] = result;
```

---

## 异常处理对比

### Python try/finally

```python
def wrapper(*args):
    self.call_stack.append(task)
    try:
        result = func(*args)
    finally:  # 即使出错也会执行
        self.call_stack.pop()
    return result
```

### C++ RAII

```cpp
// 使用 RAII 模式（更优雅）
struct StackGuard {
    std::vector<Task>& stack;
    Task task;
    
    StackGuard(std::vector<Task>& s, Task t) 
        : stack(s), task(t) {
        stack.push_back(task);
    }
    
    ~StackGuard() {  // 析构函数自动执行
        stack.pop_back();
    }
};

// 使用
auto wrapper = [](auto... args) {
    StackGuard guard(task_stack, task);  // RAII
    return func(args...);
    // guard 自动析构，栈自动弹出
};
```

---

## 内存管理对比

### Python: 自动垃圾回收

```python
# 不需要手动管理内存
cache = {}
cache[task] = result  # 自动分配
# 不再使用时自动回收
```

### C++: 手动 or 智能指针

```cpp
// 手动管理（不推荐）
Result* result = new Result();
cache[task] = result;
delete result;  // 需要手动释放

// 智能指针（推荐）
std::shared_ptr<Result> result = std::make_shared<Result>();
cache[task] = result;
// 自动释放，无需 delete
```

---

## 性能对比

### Python 的开销

```python
# 动态类型检查
x = 10
y = x + 5  # 运行时检查类型

# 函数调用开销较大
def func():
    pass

func()  # 动态分发
```

### C++ 的优势

```cpp
// 编译时类型检查
int x = 10;
int y = x + 5;  // 无运行时开销

// 内联优化
inline int func() {
    return 0;
}

func();  // 可能完全内联
```

### Contingent 的设计权衡

- **Python 版本**：灵活、简洁、易理解
- **C++ 版本**：快速、内存可控，但复杂

**选择 Python 的原因**：
- ✅ 构建系统不是性能瓶颈
- ✅ 开发速度更重要
- ✅ 代码可读性优先

---

## 迭代器和生成器

### Python 生成器

```python
def visit(task):
    visited.add(task)
    for consequence in consequences:
        if consequence not in visited:
            yield from visit(consequence)  # 递归生成
            yield consequence
```

### C++20 协程（类似）

```cpp
#include <coroutine>
#include <generator>  // C++23

std::generator<Task> visit(Task task) {
    visited.insert(task);
    for (Task consequence : consequences) {
        if (!visited.contains(consequence)) {
            for (Task t : visit(consequence)) {  // 递归
                co_yield t;
            }
            co_yield consequence;
        }
    }
}
```

### C++17 替代方案

```cpp
// 使用回调
void visit(Task task, std::function<void(Task)> callback) {
    visited.insert(task);
    for (Task consequence : consequences) {
        if (!visited.contains(consequence)) {
            visit(consequence, callback);
            callback(consequence);
        }
    }
}

// 使用
visit(task, [&results](Task t) {
    results.push_back(t);
});
```

---

## 完整的 C++ 版本框架

```cpp
#include <iostream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <functional>
#include <optional>
#include <memory>

// 简化的 Task 类型
using Task = std::pair<void*, std::string>;

class Graph {
private:
    std::unordered_map<Task, std::unordered_set<Task>> inputs_of;
    std::unordered_map<Task, std::unordered_set<Task>> consequences_of;

public:
    void add_edge(Task input, Task consequence) {
        consequences_of[input].insert(consequence);
        inputs_of[consequence].insert(input);
    }
    
    void clear_inputs_of(Task task) {
        if (auto it = inputs_of.find(task); it != inputs_of.end()) {
            for (const auto& input : it->second) {
                consequences_of[input].erase(task);
            }
            inputs_of.erase(it);
        }
    }
};

class Project {
private:
    Graph graph;
    std::unordered_map<Task, std::string> cache;
    std::vector<Task> task_stack;
    std::unordered_set<Task> todo;

public:
    template<typename Func>
    auto task(Func func) {
        return [this, func](auto... args) -> std::string {
            Task task_id = /* 创建 task */;
            
            // 记录依赖
            if (!task_stack.empty()) {
                graph.add_edge(task_id, task_stack.back());
            }
            
            // 检查缓存
            if (auto it = cache.find(task_id); it != cache.end()) {
                return it->second;
            }
            
            // 执行
            graph.clear_inputs_of(task_id);
            task_stack.push_back(task_id);
            
            std::string result;
            try {
                result = func(args...);
            } catch (...) {
                task_stack.pop_back();
                throw;
            }
            
            task_stack.pop_back();
            cache[task_id] = result;
            
            return result;
        };
    }
};
```

---

## 学习建议

### 从 C++ 到 Python 的思维转换

1. **不要想内存管理**：Python 自动处理
2. **不要想类型声明**：变量可以是任何类型
3. **拥抱鸭子类型**："如果它走起来像鸭子，叫起来像鸭子..."
4. **利用动态特性**：运行时可以改变类型

### 保留的 C++ 思维

1. **算法思维**：DFS、拓扑排序等算法是通用的
2. **数据结构**：哈希表、集合、栈的概念相同
3. **性能意识**：理解操作的时间复杂度
4. **RAII 思想**：Python 的上下文管理器类似

### 两种语言的优势互补

**C++ 适合**：
- 性能关键的系统
- 需要精确控制内存
- 编译时类型安全

**Python 适合**：
- 快速原型开发
- 脚本和自动化
- 数据处理和分析
- **构建系统**（如 Contingent）

---

*理解了这些对照，你就能用 C++ 的思维理解 Python 的实现，反之亦然。*

