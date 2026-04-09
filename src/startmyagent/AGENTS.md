# startmyagent 包知识库

**位置:** src/startmyagent/
**文件数:** 28
**子目录:** 14

## 概述
"Start My Agent" 项目的核心 Python 包，包含章节练习、示例和工具类。

## 结构
```
startmyagent/
├── chapters/          # 章节练习 (chapter1, chapter3)
├── examples/          # 入口点示例脚本
└── common/           # 共享工具类
```

## 文件查找指南
| 任务 | 位置 | 备注 |
|------|----------|-------|
| 导入包 | `import startmyagent` | 包名与目录名不同 (`start-my-agent` vs `startmyagent`) |
| 运行示例 | `examples/` | `basic_agent_usage.py` 是主入口点 |
| 核心逻辑 | `chapters/chapter1/` | `system_prompt.py` 包含智能体逻辑 |
| Transformer 实现 | `chapters/chapter3/` | 教育性质的 Transformer/BPE 实现 |
| 工具类 | `common/util/` | `markdown_reader.py` 读取提示词 |

## 包结构异常
- **缺少 `__init__.py`**: 根目录 `src/startmyagent/` 下无 `__init__.py` (非标准 Python 包结构)
- **包名不匹配**: PyPI 包名 `start-my-agent` (带连字符)，但导入为 `startmyagent` (无连字符)
- **`pyproject.toml` 配置**: 使用 `[tool.setuptools.package-dir]` 映射非标准路径

## 导入模式
**正确导入** (从已安装的包):
```python
from startmyagent.chapters.chapter1.system_prompt import get_weather
```

**错误导入** (在代码中找到):
```python
from chapters.chapter1.system_prompt import get_weather  # ❌ 错误，应为 startmyagent.chapters...
```

## 关键文件
1. `chapters/chapter1/system_prompt.py` - 核心智能体，处理天气/景点查询
2. `chapters/chapter3/transformer.py` - Transformer 实现 (有语法错误需修复)
3. `examples/basic_agent_usage.py` - 主演示脚本 (第113行有错误导入)
4. `common/util/markdown_reader.py` - 读取 Markdown 提示词的工具

## 依赖关系
- **运行时依赖**: 见根目录 `pyproject.toml`
- **开发依赖**: Black, Ruff, mypy, pytest (严格配置)
- **模型依赖**: `modelscope` (需要 `numpy`, `addict`, `transformers`)

## 注意事项
- **包未完全标准化**: 缺少 `__init__.py` 可能导致导入问题
- **混合内容**: 示例代码、学习实现、工具类在同一包内
- **教育性质**: 代码包含中文注释和 Markdown 提示词文件