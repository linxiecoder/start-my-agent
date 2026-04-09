# chapters 目录知识库

**位置:** src/startmyagent/chapters/
**文件数:** 16
**子目录:** 6
**类型:** 章节练习组织

## 概述
按课程章节组织的学习代码，包含 chapter1 (初识智能体) 和 chapter3 (大语言模型基础)。

## 结构
```
chapters/
├── chapter1/           # 第一章: 初识智能体
│   ├── system_prompt.py      # 核心智能体逻辑
│   └── ... (其他练习文件)
└── chapter3/           # 第三章: 大语言模型基础
│   ├── transformer.py        # Transformer 实现 (有语法错误)
│   ├── byte_pair_encoding.py # BPE 分词器实现
│   ├── use_llm.py           # LLM 使用示例
│   ├── exercise_for_llm.py  # LLM 练习
│   └── prompt/              # 提示词文件 (.md)
```

## 章节目录对比

### chapter1: 初识智能体
| 文件 | 用途 | 状态 |
|------|------|------|
| `system_prompt.py` | 核心智能体，处理天气/景点查询 | 功能完整 |
| `__init__.py` | 空包文件 | 存在 |

**关键功能**:
- `get_weather(city)`: 查询天气 (调用 wttr.in)
- `get_attractions(city)`: 查询景点 (模拟)
- `OpenAICompatibleClient`: 兼容 OpenAI API 的客户端

### chapter3: 大语言模型基础
| 文件 | 用途 | 状态 |
|------|------|------|
| `transformer.py` | Transformer 模型实现 | **有语法错误** |
| `byte_pair_encoding.py` | BPE 分词器实现 | 功能完整 |
| `use_llm.py` | 使用 ModelScope LLM | 依赖 `modelscope` |
| `exercise_for_llm.py` | LLM 练习 | 有 LSP 错误 |
| `prompt/system_prompt.md` | 系统提示词 | 静态文件 |
| `prompt/user_prompt.md` | 用户提示词 | 静态文件 |

## 关键问题

### 1. `transformer.py` 语法错误
**位置:** `src/startmyagent/chapters/chapter3/transformer.py`
**问题:**
- 第28行: `super.__init__()` 应为 `super().__init__()`
- 第139-140行: `MultiHeadAttention()` 和 `PositionWiseFeedForward()` 缺少参数
- 第162-164行: DecoderLayer 同样问题

**影响:** 代码无法运行，会抛出 TypeError。

### 2. 导入问题
在 `examples/basic_agent_usage.py` 第113行:
```python
from chapters.chapter1.system_prompt import get_weather, get_attractions  # ❌ 错误
```
应为:
```python
from startmyagent.chapters.chapter1.system_prompt import get_weather, get_attractions  # ✅ 正确
```





## 使用指南
- **chapter1**: `from startmyagent.chapters.chapter1.system_prompt import get_weather`
- **chapter3**: 需先修复 `transformer.py` 语法错误

## 维护优先级
1. 修复 `transformer.py` 语法错误 (第28, 139-140, 162-164行)
2. 修复 `basic_agent_usage.py` 第113行导入