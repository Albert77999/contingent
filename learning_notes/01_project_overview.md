# Contingent 项目学习笔记 - 01：项目概览

## 学习背景

- **学习者**：C++ 背景的大学生，刚学完 Python 基础语法
- **项目**：Contingent - 一个完全动态的构建系统（来自《500 Lines or Less》）
- **学习时间**：已投入 4+ 小时阅读文档

## 项目核心理念

Contingent 解决了传统构建系统（如 Make、Sphinx）的两个关键问题：

1. **重建太多** - 对小改动做了不必要的重建
2. **重建太少** - 遗漏了需要更新的交叉引用，导致输出不一致

### 核心特性

- ✅ 自动学习任务之间的依赖关系
- ✅ 基于返回值而非文件时间戳判断是否重建
- ✅ 最小化重建工作
- ✅ 处理动态依赖（交叉引用可能变化）

## 项目结构

```
contingent/
├── code/
│   ├── contingent/          # 核心库（~300行代码）
│   │   ├── graphlib.py      # 图数据结构（107行）
│   │   ├── projectlib.py    # 项目调度器（213行）
│   │   ├── rendering.py     # Graphviz 可视化（45行）
│   │   └── io.py            # 文件监控（59行）
│   ├── example/
│   │   └── blog_project.py  # 博客系统示例
│   └── posts/               # 示例文章
├── contingent.markdown      # 完整章节文档（1592行）
└── venv/                    # Python 虚拟环境
```

## 核心架构

### 1. Graph 模块 (graphlib.py)
- 使用 `defaultdict(set)` 实现有向图
- 双向存储边：`_inputs_of` 和 `_consequences_of`
- 支持拓扑排序的递归后果追踪

### 2. Project 模块 (projectlib.py)
- 核心构建调度器
- 关键数据结构：
  - `_graph`: 任务依赖图
  - `_cache`: 任务返回值缓存
  - `_task_stack`: 执行栈
  - `_todo`: 待重建任务集合

### 3. 装饰器模式
`@task` 装饰器自动追踪任务间的调用关系

## 已完成的环境配置

### 问题修复
1. ✅ nbformat API 兼容性（`reads_json()` → `reads()`）
2. ✅ docutils API 更新（`traverse()` → `findall()`）
3. ✅ 保留 Notebook v3 元数据

### 依赖安装
```bash
pip install docutils nbformat nbconvert jinja2
```

### 生成的文件
- `code/output/intro.html`
- `code/output/addition.html`
- `code/output/subtraction.html`
- `code/output/retrospective.html`

## Python vs C++ 对比

作为 C++ 程序员的优势：
- ✅ 理解数据结构（图、哈希表、栈）
- ✅ 理解指针/引用概念
- ✅ 理解函数调用栈
- ✅ 理解对象的身份

需要适应的 Python 特性：
- ⚠️ 装饰器（Python 特有）
- ⚠️ 动态类型
- ⚠️ 一切皆对象

## 学习策略

采用分阶段学习，每个阶段 2-3 小时：
1. 数据结构深度剖析
2. 装饰器机制深度理解
3. 重建算法深度分析
4. 实战扩展
5. 设计思考

## 下一步

继续深入学习装饰器机制和核心算法。

