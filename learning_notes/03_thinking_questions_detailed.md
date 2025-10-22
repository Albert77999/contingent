# Contingent 项目学习笔记 - 03：三个核心思考题详解

## 思考题1：为什么用 `Task(wrapper, args)` 而不是 `(func.__name__, args)`？

### 简短答案
函数对象是唯一的身份标识，函数名可能重复。

### 详细解答

#### 原因1：函数对象的身份 vs 函数名称

```python
# 问题：同名函数
def process(data):
    return data.upper()

# 后来重新定义
def process(data):
    return data.lower()  # 完全不同的实现！

# 使用函数名：无法区分两个不同的函数
# 使用函数对象：每个函数有唯一的 id
```

#### 原因2：装饰器包装后的函数引用

```python
# Contingent 中的实际情况
@wraps(task_function)
def wrapper(*args):
    task = Task(wrapper, args)  # 使用 wrapper，不是 task_function
```

为什么用 wrapper？
- wrapper 就是被缓存和调用的那个函数
- 用户调用的是 wrapper，不是原始函数
- 需要用 wrapper 作为身份标识

#### 原因3：支持 lambda 和匿名函数

```python
# lambda 的 __name__ 都是 '<lambda>'
task1 = task(lambda x: x * 2)
task2 = task(lambda x: x * 3)

# 使用函数名：('lambda', (5,)) == ('lambda', (5,)) ❌
# 使用函数对象：(task1, (5,)) != (task2, (5,)) ✓
```

#### 原因4：哈希和相等性检查

```python
class Task(namedtuple('Task', ('task_function', 'args'))):
    # namedtuple 自动提供：
    # - __hash__(): 基于 (task_function, args) 的哈希
    # - __eq__(): 基于两个字段的相等性比较
    # - 可以作为 dict 的 key 和 set 的元素
    
    def __new__(cls, task_function, args):
        try:
            hash(args)  # 确保参数可哈希
        except TypeError as e:
            raise ValueError('arguments must be hashable')
        return super().__new__(cls, task_function, args)
```

### C++ 对比

```cpp
// C++ 中函数指针也有唯一地址
void func1() { }
void func2() { }

std::cout << (void*)func1 << std::endl;  // 不同地址
std::cout << (void*)func2 << std::endl;

// Python 的函数对象类似
```

### 实际影响

如果用函数名：
- ❌ 两个项目中的同名函数会冲突
- ❌ 重新定义函数会导致缓存错误
- ❌ lambda 函数无法区分
- ❌ 无法处理动态创建的函数

用函数对象：
- ✅ 每个函数有唯一标识
- ✅ 重定义函数不影响旧缓存
- ✅ 支持所有类型的可调用对象
- ✅ 自然支持哈希

---

## 思考题2：为什么需要 `clear_inputs_of()` 在第89行？

### 简短答案
处理动态依赖的变化 - 任务的输入可能在不同执行中改变。

### 详细解答

#### 问题场景：条件依赖

```python
use_cache = True

@task
def get_data():
    if use_cache:
        return read_cache()  # 第一次执行：依赖 read_cache
    else:
        return read_file("data.txt")  # 第二次执行：依赖 read_file
```

**如果不清除旧依赖**：
```
第一次执行：get_data → read_cache
第二次执行：get_data → read_file
         但旧的边还在：get_data → read_cache ❌

结果：get_data 同时依赖两个任务！
```

#### 真实场景：文档交叉引用

```python
# api.rst 第一版
"""
API Reference
=============
See also: tutorial.rst
See also: guide.rst
"""

# render('api.rst') 依赖于：
# - title_of('tutorial.rst')
# - title_of('guide.rst')

# 用户编辑，删除了对 guide.rst 的引用
"""
API Reference
=============
See also: tutorial.rst
"""

# 如果不清除旧边：
# render('api.rst') 仍然依赖 title_of('guide.rst')
# guide.rst 改变时，api.html 会被误重建！
```

#### clear_inputs_of() 的执行时机

```python
# projectlib.py 第88-95行
if return_value is _unavailable:
    self._graph.clear_inputs_of(task)  # ← 在这里！
    self._task_stack.append(task)
    try:
        return_value = task_function(*args)
    finally:
        self._task_stack.pop()
    self.set(task, return_value)
```

**为什么在这个位置？**
1. **确认需要重新执行**：只有缓存失效时才清除
2. **在执行前清除**：给任务一个"干净"的起点
3. **让新的依赖被正确记录**：执行过程中会重新添加边

#### 实际效果

```python
# graphlib.py 第55-59行
def clear_inputs_of(self, task):
    """Remove all edges leading to `task` from its previous inputs."""
    input_tasks = self._inputs_of.pop(task, ())
    for input_task in input_tasks:
        self._consequences_of[input_task].remove(task)
```

**操作**：
1. 获取 task 的所有输入任务
2. 从每个输入任务的后果集合中移除 task
3. 清空 task 的输入集合

### C++ 对比

```cpp
// 类似于智能指针的引用计数更新
// 旧的依赖关系需要"解引用"
void clear_inputs_of(Task* task) {
    for (auto input : task->inputs) {
        input->consequences.erase(task);  // 双向删除
    }
    task->inputs.clear();
}
```

### 关键理解

- **动态依赖**：任务的输入不是固定的，可能根据条件改变
- **精确追踪**：只保留实际使用的依赖关系
- **避免误重建**：删除的引用不应该触发重建

---

## 思考题3：为什么用 `_unavailable` 而不是 `None`？

### 简短答案
任务可能合法地返回 `None`，需要一个唯一的哨兵对象来区分"未找到"和"值是None"。

### 详细解答

#### 问题演示

```python
# 错误的实现
def _get_from_cache_bad(self, task):
    return self._cache.get(task, None)  # ❌

# 使用
if result is None:  # 有歧义！
    # 是缓存未命中？还是缓存的值就是 None？
    pass
```

**实际问题**：

```python
@task
def check_file_exists(filename):
    """检查文件是否存在"""
    if not os.path.exists(filename):
        return None  # 文件不存在，返回 None

# 第一次调用
result = check_file_exists("missing.txt")  # 返回 None，被缓存

# 第二次调用
cached = cache.get(task, None)  # 得到 None
if cached is None:  # True，但这是缓存值，不是未命中！
    # 错误：重新执行了任务
```

#### 正确的实现：哨兵对象

```python
# projectlib.py 第9行
_unavailable = object()  # 唯一的哨兵对象

# 第101-112行
def _get_from_cache(self, task):
    if not self._cache_on:
        return _unavailable
    if task in self._todo:
        return _unavailable
    return self._cache.get(task, _unavailable)  # ✓

# 第88行
if return_value is _unavailable:  # 清晰的语义
    # 缓存未命中，执行任务
```

#### 哨兵对象的特性

```python
# 1. 唯一性
sentinel1 = object()
sentinel2 = object()
print(sentinel1 is sentinel2)  # False，每个都是唯一的

# 2. 不等于任何值
_unavailable = object()
possible_values = [None, 0, False, "", [], {}, set()]
for val in possible_values:
    assert _unavailable is not val  # 全部通过

# 3. 使用 is 比较（身份检查）
if result is _unavailable:  # 非常快，且语义清晰
    pass

# 4. 不可能是用户的返回值
# 用户无法构造出相同的 object()
```

#### 为什么 `object()` 完美？

```python
# object() 是最纯粹的对象
_unavailable = object()

# 没有任何特殊方法
dir(_unavailable)  # 只有基本的 __class__, __eq__ 等

# 唯一的用途就是作为哨兵
# 用户不可能"意外"返回这个对象
```

### Contingent 的三种使用场景

```python
# 场景1: 检查缓存
return_value = self._get_from_cache(task)
if return_value is _unavailable:  # 缓存未命中
    # 执行任务

# 场景2: 追踪记录
def _add_task_to_trace(self, task, return_value):
    not_available = (return_value is _unavailable)
    # 区分是执行了任务还是使用了缓存

# 场景3: 默认返回值
return self._cache.get(task, _unavailable)
# 不在缓存中时返回哨兵
```

### 方案对比表

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| `None` | 简单 | 无法区分"返回None"和"未找到" | 已知不会返回None |
| `-1` 或特殊值 | 简单 | 可能是合法返回值 | 数值类型 |
| 字符串如 `"NOT_FOUND"` | 可读 | 可能是合法返回值 | 已知返回类型 |
| 抛出异常 | 清晰 | 性能差，控制流复杂 | 真正的错误情况 |
| `object()` | **完美** | 需要理解概念 | **任何需要哨兵的场景** ✓ |

### C++ 对比

```cpp
// C++17 的 std::optional 类似概念
std::optional<int> get_from_cache(Key key) {
    auto it = cache.find(key);
    if (it == cache.end()) {
        return std::nullopt;  // 类似 _unavailable
    }
    return it->second;  // 可能是任何值，包括 0
}

// 使用
auto result = get_from_cache(key);
if (!result.has_value()) {  // 类似 is _unavailable
    // 缓存未命中
}
```

### Python 的最佳实践

这是 **Sentinel Object Pattern**（哨兵对象模式）：

```python
# Python 标准库中的应用

# 1. itertools.takewhile 中的哨兵
_marker = object()

# 2. functools.lru_cache 中的哨兵
_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])

# 3. 很多库都用 object() 作为默认参数
def function(arg=object()):
    # 如果 arg is object()，说明用户没传参数
    pass
```

---

## 总结

### 三个问题的本质

1. **Task(wrapper, args)**：身份标识的唯一性
2. **clear_inputs_of()**：动态依赖的正确性
3. **_unavailable**：哨兵对象的必要性

### 设计哲学

这三个设计都体现了：
- ✅ **正确性优先**：宁可复杂，不要出错
- ✅ **处理边界情况**：考虑所有可能性
- ✅ **优雅的抽象**：概念清晰，易于理解

### Python vs C++

| 概念 | Python | C++ |
|------|--------|-----|
| 唯一标识 | 对象 id | 对象地址 |
| 可选值 | `_unavailable` | `std::optional` |
| 动态依赖 | 运行时更新 | 编译时确定 |

---

*这三个问题触及了 Contingent 设计的精髓，理解它们就理解了整个系统的核心思想。*

