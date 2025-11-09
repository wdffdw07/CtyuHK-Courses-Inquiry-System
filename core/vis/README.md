# Visualization Layer (core/vis) - 模块拆分说明

## 📁 新的模块结构

vis 层已经从单一的 `graph.py` 文件拆分为三个独立模块：

### 1. `common.py` - 共享工具模块
**职责**：提供所有可视化功能共用的基础工具
- `load_relations(db_path)` - 从数据库加载课程和前置关系
- `load_exclusions(db_path)` - 加载互斥课程映射
- `build_graph(courses, edges)` - 构建 networkx 有向图

### 2. `dependency.py` - 依赖图生成模块
**职责**：生成课程依赖关系图（有前置课程的图）
- `render_dependency_tree()` - 主渲染函数
- `find_roots()` - 查找根节点（无前置课程的课程）
- `detect_cycles()` - 检测循环依赖
- `layered_layout()` - 分层布局算法

**功能特性**：
- ✅ 循环依赖检测和高亮（红色边）
- ✅ Focus 模式（只显示某课程的前置链）
- ✅ 深度限制（max_depth）
- ✅ 分层布局（layered layout）
- ✅ 按开课单位着色
- ✅ 标题截断
- ✅ 排除孤立节点
- ✅ 直边/曲边选项

### 3. `roots.py` - 无依赖图生成模块
**职责**：生成无依赖课程图（既无前置也无依赖的终端课程）
- `render_root_courses()` - 主渲染函数

**功能特性**：
- ✅ 网格布局（grid layout）
- ✅ 按开课单位着色
- ✅ 显示前置课程状态
- ✅ 可配置每行最大节点数

### 4. `graph.py` - **向后兼容包装器**
为了保持向后兼容性，`graph.py` 现在作为一个包装器（wrapper），重新导出所有功能。

**旧代码无需修改**：
```python
# 这样的旧代码仍然能正常工作
from core.vis.graph import render_dependency_tree, render_root_courses
```

**推荐新代码使用**：
```python
# 新代码推荐直接从专用模块导入
from core.vis.dependency import render_dependency_tree
from core.vis.roots import render_root_courses
from core.vis.common import load_relations, build_graph
```

### 5. `__init__.py` - 包导出
所有公共函数都在包级别导出，可以这样使用：
```python
from core.vis import render_dependency_tree, render_root_courses
```

## 🎯 拆分的好处

### 1. **职责分离**
- 依赖图生成逻辑 → `dependency.py`
- 无依赖图生成逻辑 → `roots.py`  
- 共享工具函数 → `common.py`

### 2. **更易维护**
- 修改依赖图功能不会影响无依赖图
- 每个文件职责单一，代码更清晰
- 更容易定位和修复 bug

### 3. **更易测试**
- 可以独立测试每个模块
- 共享工具函数可以单独测试
- 减少测试之间的耦合

### 4. **更易扩展**
- 添加新的可视化类型时只需新建文件
- 不会让单个文件变得过大
- 共享逻辑可以复用

### 5. **向后兼容**
- 旧代码无需修改
- `graph.py` 作为兼容层继续存在
- 逐步迁移到新结构

## 📊 文件大小对比

**重构前**：
- `graph.py`: ~500 行（所有功能混在一起）

**重构后**：
- `common.py`: ~75 行（共享工具）
- `dependency.py`: ~280 行（依赖图专用）
- `roots.py`: ~110 行（无依赖图专用）
- `graph.py`: ~20 行（兼容包装器）

## 🔄 调用流程

### 依赖图生成流程：
```
orchestrator.cmd_visualize()
    ↓
dependency.render_dependency_tree()
    ↓
common.load_relations() + common.load_exclusions()
    ↓
common.build_graph()
    ↓
dependency.layered_layout() + dependency.detect_cycles()
    ↓
matplotlib 渲染输出
```

### 无依赖图生成流程：
```
orchestrator.cmd_visualize()
    ↓
roots.render_root_courses()
    ↓
common.load_relations()
    ↓
common.build_graph()
    ↓
roots 网格布局
    ↓
matplotlib 渲染输出
```

## ✅ 测试验证

已通过测试：
- ✅ 依赖图生成（v020/dependency_v020.png）
- ✅ 无依赖图生成（v020/roots_only_v020.png）
- ✅ 配置文件加载正常
- ✅ 所有模块无语法错误
- ✅ 向后兼容性保持

---

**创建时间**: 2025-11-09  
**重构原因**: 将 vis 层拆分为独立模块，提高可维护性和可扩展性  
**状态**: ✅ 完成并测试通过
