# 🎓 Contingent 学习指南

## 你刚才看到了什么？

恭喜！你已经成功运行了一个**动态构建系统**，它生成了4个HTML文件。

### 📂 生成的文件

查看 `../output/` 目录：
- `intro.html` - 简单的RST转HTML
- `addition.html` - Jupyter Notebook转HTML  
- `subtraction.html` - Jupyter Notebook转HTML
- `retrospective.html` - 包含交叉引用的RST

## 🔍 关键观察点

### 1. 原始程序的设计

`blog_project.py` 的 `render()` 函数：
```python
def render(paths, path):
    # ... 生成HTML内容 ...
    print('-' * 72)
    print(text)  # ← 只打印到控制台
    return text  # ← 返回HTML字符串，但不保存
```

**这是一个演示程序**，只是展示Contingent如何工作，并不真正保存文件！

### 2. 我创建的增强版本

`demo_html_generation.py` 增加了文件保存功能：
```python
def main():
    for path in sorted_posts(paths):
        html_content = render(paths, path)
        
        # 生成输出文件名
        output_name = basename[:-4] + '.html'
        
        # 保存到文件 ← 新增的功能
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
```

## 📊 Contingent 的智能之处

### 观察交叉引用

打开 `retrospective.html`，你会看到：

```html
<p>Having looked at <i>One Thing About Addition</i>
and <i>The Terror of Subtraction</i>
in our previous two blog posts...</p>
```

这些标题是从哪里来的？

在源文件 `retrospective.rst` 中：
```rst
Having looked at title_of(addition.ipynb)
and title_of(subtraction.ipynb)
```

**Contingent 自动：**
1. 解析了 `addition.ipynb` 获取标题
2. 解析了 `subtraction.ipynb` 获取标题  
3. 记录了依赖关系
4. 替换了交叉引用

### 依赖图示例

```
retrospective.rst
    ↓ 调用 body_of()
    ↓ 调用 title_of(addition.ipynb)
    ↓     ↓ 调用 parse(addition.ipynb)
    ↓     ↓     ↓ 调用 read_text_file(addition.ipynb)
    ↓ 调用 title_of(subtraction.ipynb)
          ↓ 调用 parse(subtraction.ipynb)
              ↓ 调用 read_text_file(subtraction.ipynb)
```

## 🧪 实验：观察智能重建

### 实验 1：修改文章内容（不影响标题）

1. 打开 `../posts/intro.rst`
2. 修改正文内容（不是标题）
3. 保存
4. 运行：`python demo_html_generation.py`

**观察**：只有 `intro.html` 被重建

### 实验 2：修改文章标题（影响其他文章）

1. 打开 `../posts/addition.ipynb`
2. 在 metadata 中修改 "name": "One Thing About Addition" 为其他内容
3. 保存  
4. 运行：`python demo_html_generation.py`

**观察**：`addition.html` 和 `retrospective.html` 都被重建！

### 实验 3：查看依赖图

运行这个脚本查看完整的依赖关系：

```python
from blog_project import project
from contingent.rendering import as_graphviz

# 显示依赖图
for edge in project._graph.edges():
    print(f"{edge[0]} -> {edge[1]}")
```

## 📚 深入学习路径

### 阶段 1：理解数据结构（30分钟）

阅读并实验：

**`code/contingent/graphlib.py`** - 图的实现
```python
# 核心数据结构
self._inputs_of = defaultdict(set)
self._consequences_of = defaultdict(set)

# 添加边
def add_edge(self, input_task, consequence_task):
    self._consequences_of[input_task].add(consequence_task)
    self._inputs_of[consequence_task].add(input_task)
```

**实验**：
```python
from contingent.graphlib import Graph

g = Graph()
g.add_edge('A', 'B')
g.add_edge('B', 'C')
g.add_edge('A', 'C')

print("A的后果:", g.immediate_consequences_of('A'))
print("递归后果:", g.recursive_consequences_of(['A']))
```

### 阶段 2：理解装饰器（30分钟）

阅读 **`code/contingent/projectlib.py`** 的 `@task` 装饰器

**关键代码**：
```python
def task(self, task_function):
    @wraps(task_function)
    def wrapper(*args):
        task = Task(wrapper, args)
        
        # 1. 记录调用关系
        if self._task_stack:
            self._graph.add_edge(task, self._task_stack[-1])
        
        # 2. 检查缓存
        return_value = self._get_from_cache(task)
        
        if return_value is _unavailable:
            # 3. 执行任务
            self._task_stack.append(task)
            try:
                return_value = task_function(*args)
            finally:
                self._task_stack.pop()
            
            # 4. 保存结果
            self.set(task, return_value)
        
        return return_value
    return wrapper
```

**实验**：添加打印语句观察执行流程

### 阶段 3：构建自己的示例（60分钟）

创建一个简单的博客系统：

```python
from contingent.projectlib import Project

project = Project()
task = project.task

# 你的任务定义
@task
def read_markdown(filename):
    with open(filename) as f:
        return f.read()

@task
def convert_to_html(filename):
    content = read_markdown(filename)
    # 简单的markdown转换
    return f"<html><body>{content}</body></html>"

# 使用
html = convert_to_html("test.md")
```

## 🎯 学习检查点

完成以下检查点，确保理解：

### 基础理解
- [ ] 理解为什么需要动态构建系统
- [ ] 能解释 `defaultdict(set)` 如何存储图
- [ ] 理解装饰器如何拦截函数调用
- [ ] 知道什么是任务栈

### 实践能力  
- [ ] 能够修改源文件并观察重建行为
- [ ] 能够解释为什么某些文件被重建
- [ ] 能够查看和理解依赖图
- [ ] 能够添加新的任务函数

### 高级理解
- [ ] 理解缓存机制如何工作
- [ ] 理解拓扑排序的作用
- [ ] 能够解释增量构建的原理
- [ ] 能够设计自己的构建系统

## 🔧 常用调试技巧

### 1. 启用详细输出

```python
project.verbose = True
```

### 2. 追踪任务执行

```python
project.start_tracing()
# ... 执行任务 ...
print(project.stop_tracing(verbose=True))
```

### 3. 检查缓存

```python
print("缓存的任务:", list(project._cache.keys()))
```

### 4. 查看待办列表

```python
print("需要重建:", project._todo)
```

## 🚀 进阶挑战

1. **添加CSS支持**：为生成的HTML添加样式
2. **添加索引页**：生成一个列出所有文章的index.html
3. **添加搜索功能**：支持全文搜索
4. **优化性能**：测量不同场景的构建时间
5. **扩展格式**：支持Markdown文件

## 📖 推荐阅读顺序

1. `contingent.markdown` - 完整理论（2小时）
2. `code/contingent/graphlib.py` - 实现细节（30分钟）
3. `code/contingent/projectlib.py` - 核心逻辑（1小时）
4. `code/example/blog_project.py` - 实际应用（30分钟）
5. 动手实验 - 修改和扩展（2-3小时）

## 🎓 总结

Contingent 的核心思想：

1. **任务即函数** - 每个构建步骤是一个函数
2. **自动追踪** - 装饰器自动记录依赖关系
3. **智能缓存** - 只重建真正需要的部分
4. **基于值** - 根据返回值而非时间戳判断是否重建

这是一个优雅的设计，代码简洁但功能强大！

---

**下一步**：尝试修改源文件，观察Contingent的智能重建行为！ 🚀

