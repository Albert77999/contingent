# Contingent 项目学习笔记 - 04：图算法深度解析

## 循环依赖问题

### 问题：如果图中有循环依赖会怎样？

**简短答案**：图遍历算法可以处理，但任务执行会陷入无限递归。

### 两种循环的区别

#### 1️⃣ 图结构的循环（Contingent 可以处理）

```python
# 依赖图中的环
g.add_edge('A', 'B')
g.add_edge('B', 'C')
g.add_edge('C', 'A')  # 形成环：A → B → C → A
```

**算法如何处理**：

```python
def recursive_consequences_of(self, tasks, include=False):
    def visit(task):
        visited.add(task)  # ← 立即标记为已访问
        consequences = self._consequences_of[task]
        for consequence in self.sorted(consequences, reverse=True):
            if consequence not in visited:  # ← 跳过已访问的节点
                yield from visit(consequence)
                yield consequence
    
    visited = set()  # 关键：防止重复访问
    # ...
```

**执行过程**（以 A→B→A 为例）：

```
1. visit(A)
   visited = {A}
   
2. A 的后果是 B，访问 visit(B)
   visited = {A, B}
   
3. B 的后果是 A，检查：A in visited？
   True！跳过，不再递归
   
4. 返回 [B]
```

**关键代码**（graphlib.py 第92-95行）：

```python
def visit(task):
    visited.add(task)  # 92行：立即标记
    consequences = self._consequences_of[task]
    for consequence in self.sorted(consequences, reverse=True):
        if consequence not in visited:  # 95行：检查
            yield from visit(consequence)
            yield consequence
```

#### 2️⃣ 任务执行的循环（Contingent 无法处理）

```python
@task
def task_a():
    return task_b()  # 调用 B

@task
def task_b():
    return task_a()  # 调用 A，形成执行循环
```

**为什么无法处理**：
- 这是真正的函数递归调用
- Python 有递归深度限制（默认 ~1000）
- 会导致 `RecursionError`

**执行过程**：

```
task_a()
  → task_b()
    → task_a()  # 又回到 A
      → task_b()  # 又回到 B
        → task_a()  # 无限循环
          ...
RecursionError: maximum recursion depth exceeded
```

### visited 集合的作用

**经典的图遍历算法**（DFS深度优先搜索）：

```python
def dfs(graph, start):
    visited = set()  # 记录已访问节点
    
    def visit(node):
        if node in visited:  # 已访问过，直接返回
            return
        
        visited.add(node)  # 标记为已访问
        print(f"访问: {node}")
        
        for neighbor in graph[node]:
            visit(neighbor)  # 递归访问邻居
    
    visit(start)
```

**C++ 对比**：

```cpp
void dfs(const Graph& graph, int start) {
    std::unordered_set<int> visited;
    
    std::function<void(int)> visit = [&](int node) {
        if (visited.count(node)) return;  // 已访问
        
        visited.insert(node);  // 标记
        std::cout << "访问: " << node << std::endl;
        
        for (int neighbor : graph[node]) {
            visit(neighbor);  // 递归
        }
    };
    
    visit(start);
}
```

### 实验：观察循环处理

```python
from contingent.graphlib import Graph

g = Graph()

# 构建循环：A → B → C → A
g.add_edge('A', 'B')
g.add_edge('B', 'C')
g.add_edge('C', 'A')

print("图中有循环：A → B → C → A")
print("\n从 A 开始的递归后果:")
result = g.recursive_consequences_of(['A'])
print(result)

# 输出: ['B', 'C']
# 说明：每个节点只访问一次，A 被跳过了
```

---

## 拓扑排序算法

### recursive_consequences_of 的实现

这是一个**修改版的拓扑排序**：

```python
def recursive_consequences_of(self, tasks, include=False):
    """返回拓扑排序的后果列表"""
    
    def visit(task):
        visited.add(task)  # 标记为已访问
        consequences = self._consequences_of[task]
        
        # 倒序遍历（为了最后反转时顺序正确）
        for consequence in self.sorted(consequences, reverse=True):
            if consequence not in visited:
                yield from visit(consequence)  # 递归访问
                yield consequence  # 后序遍历
    
    def generate_consequences_backwards():
        for task in self.sorted(tasks, reverse=True):
            yield from visit(task)
            if include:
                yield task
    
    visited = set()
    return list(generate_consequences_backwards())[::-1]  # 反转
```

### 为什么要倒序然后反转？

**关键**：保证依赖关系的正确顺序。

**示例**：

```
依赖图:
  A → B → D
  A → C → D

期望顺序: [B, C, D] 或 [C, B, D]
关键: D 必须在 B 和 C 之后
```

**算法步骤**：

```python
# 1. 倒序访问 [A]
visit(A):
    # 2. 倒序访问 A 的后果 [C, B]（假设排序后是这个顺序）
    visit(C):
        # 3. 访问 C 的后果 [D]
        visit(D):
            # 4. D 无后果，返回
        yield D  # 生成 D
    yield C  # 生成 C
    
    visit(B):
        # D 已在 visited 中，跳过
    yield B  # 生成 B

# 5. 生成顺序: [D, C, B]
# 6. 反转: [B, C, D] ✓
```

### 后序遍历的特性

```python
def visit(task):
    visited.add(task)
    for consequence in consequences:
        if consequence not in visited:
            yield from visit(consequence)  # 先递归
            yield consequence  # 后生成（后序）
```

**后序遍历**保证：
- 节点在其所有后继节点之后生成
- 反转后，节点在其所有后继节点之前
- 这就是拓扑排序！

### C++ 实现对比

```cpp
vector<Task> topological_sort(const Graph& graph, const set<Task>& tasks) {
    unordered_set<Task> visited;
    vector<Task> result;
    
    function<void(Task)> visit = [&](Task task) {
        visited.insert(task);
        
        for (Task consequence : graph.consequences_of(task)) {
            if (visited.find(consequence) == visited.end()) {
                visit(consequence);  // 递归
            }
        }
        
        result.push_back(task);  // 后序添加
    };
    
    for (Task task : tasks) {
        if (visited.find(task) == visited.end()) {
            visit(task);
        }
    }
    
    reverse(result.begin(), result.end());  // 反转
    return result;
}
```

---

## 手动追踪算法执行

### 复杂图示例

```
依赖图:
  A → D
  B → E
  C → F
  A → G
  B → H
  C → I
  G → E
  I → E

问题: 如果 A 改变，需要重建什么？
```

### 手动追踪

```python
# 调用: recursive_consequences_of(['A'])

visited = set()

# 1. visit(A)
visited = {A}
A 的后果: [D, G]

  # 2. visit(G)（假设倒序后 G 在前）
  visited = {A, G}
  G 的后果: [E]
  
    # 3. visit(E)
    visited = {A, G, E}
    E 的后果: []
    yield E
  
  yield G
  
  # 4. visit(D)
  visited = {A, G, E, D}
  D 的后果: []
  yield D

# 生成顺序（后序）: E, G, D
# 反转后: D, G, E ✓

# 验证: D 和 G 都是 A 的直接后果
#      E 依赖于 G，所以在 G 之后
```

### 为什么这个顺序正确？

```python
# 重建顺序: [D, G, E]

# 执行 D: 需要 A（已经重建了）✓
# 执行 G: 需要 A（已经重建了）✓
# 执行 E: 需要 G 和 B
#         G 已经重建了 ✓
#         B 没变，用缓存 ✓
```

---

## 为什么需要拓扑排序？

### 场景：博客系统

```python
# 依赖关系
read('tutorial.rst') 
  → parse('tutorial.rst')
    → title_of('tutorial.rst')
      → render('api.rst')  # api.rst 引用了 tutorial 的标题

# 如果 tutorial.rst 改变了:
需要按顺序执行:
  1. read('tutorial.rst')
  2. parse('tutorial.rst')  
  3. title_of('tutorial.rst')
  4. render('api.rst')

# 如果乱序执行:
  1. render('api.rst')  # 失败！title_of 还没更新
  2. title_of(...)
  3. parse(...)
  4. read(...)
```

### Contingent 的保证

```python
# rebuild() 方法（projectlib.py 第175-178行）
while self._todo:
    tasks = self._graph.recursive_consequences_of(self._todo, True)
    # tasks 已经按拓扑顺序排列
    for function, args in tasks:
        function(*args)  # 按正确顺序执行
```

**保证**：
- ✅ 每个任务执行时，它的所有输入都已经更新
- ✅ 避免使用过期的缓存值
- ✅ 保持输出的一致性

---

## 算法复杂度

### 时间复杂度

```python
# recursive_consequences_of()
# V = 节点数，E = 边数

visited = set()  # O(1) 查找
for each task:  # O(V)
    visit(task)
        for each consequence:  # O(E)
            if not visited:
                visit(consequence)

# 总计: O(V + E) - 标准的 DFS 复杂度
```

### 空间复杂度

```python
# visited 集合: O(V)
# 递归栈: O(V) 最坏情况（链式依赖）
# 总计: O(V)
```

### C++ 对比

```cpp
// 完全相同的复杂度
// DFS 是语言无关的算法
```

---

## 关键要点总结

### 1. visited 集合的作用

- ✅ 防止重复访问节点
- ✅ 处理图中的循环
- ✅ 保证算法终止

### 2. 后序遍历的目的

- ✅ 保证拓扑序
- ✅ 节点在后继之后生成
- ✅ 反转后得到正确顺序

### 3. 两种循环的区别

- **图循环**：算法可以处理（visited 集合）
- **执行循环**：会导致无限递归

### 4. 拓扑排序的必要性

- ✅ 保证依赖顺序正确
- ✅ 避免使用过期数据
- ✅ 维护系统一致性

---

*理解了这个算法，你就掌握了 Contingent 的核心数据结构操作。*

