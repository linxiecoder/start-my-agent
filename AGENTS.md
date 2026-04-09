# 项目知识库

**生成时间:** 2026-04-03 (init-deep更新)
**提交版本:** 无 (尚未提交)
**分支:** master

## 概述
Python 学习项目，用于 AI/LLM 智能体开发 ("Start My Agent" 课程)。这是一个教育性质的代码库，包含练习代码，不是生产应用程序。

## 项目结构
```
StartMyAgent/
├── src/startmyagent/       # 主要代码包 (Python 包)
│   ├── chapters/          # 章节练习 (chapter1, chapter3)
│   ├── examples/          # 入口点和演示
│   └── common/            # 共享工具
├── learning/notes/         # 学习笔记 (中文 Markdown)
├── project/               # 课程设计模板 (空)
├── tests/                 # 测试用例
├── .venv/                 # Python 虚拟环境
├── .idea/                 # PyCharm/IntelliJ 配置
├── pyproject.toml         # Python 项目配置
├── requirements.txt       # 依赖清单
└── README.md             # 项目说明
```

## 文件查找指南
| 任务 | 位置 | 备注 |
|------|----------|-------|
| 运行演示 | `src/startmyagent/examples/` | `basic_agent_usage.py` 是主要入口点 |
| 核心智能体逻辑 | `src/startmyagent/chapters/chapter1/system_prompt.py` | 主要智能体实现 |
| Transformer/BPE 代码 | `src/startmyagent/chapters/chapter3/` | 学习实现 |
| 工具类 | `src/startmyagent/common/util/` | `markdown_reader.py` 用于读取提示词 |
| 课程指南 | `project/README.md` | 建议的项目结构 |
| 学习笔记 | `learning/notes/` | 中文课程资料 |

## 代码地图
*无 LSP 数据可用 - 项目使用 Python 但缺少正确的包结构。*

关键模块:
- **`startmyagent.chapters.chapter1.system_prompt`**: 与 LLM 交互的核心智能体
- **`startmyagent.chapters.chapter3.transformer`**: Transformer 模型实现 (教育性质)
- **`startmyagent.chapters.chapter3.byte_pair_encoding`**: BPE 分词器实现
- **`startmyagent.common.util.markdown_reader`**: 读取 Markdown 提示词的工具类

## 代码规范
**格式化/检查配置 (pyproject.toml)**:
- **Black**: line-length = 88, target-version = py38
- **Ruff**: 启用 E/F/W/I/N/UP/YTT 规则，__init__.py 允许 F401 (未使用导入)
- **mypy**: 严格类型检查 (无未注解函数、检查未注解定义、无隐式 Optional 等)
- **pytest**: 严格模式 (--strict-markers, --strict-config), 短回溯格式

这是一个学习项目，但配置了严格的质量工具。

**与标准 Python 项目的差异:**
1. **已修复** - 现在有 `src/` 目录 - 代码位于 `src/startmyagent/` 中
2. **已修复** - 现在有 `pyproject.toml` - 是可安装的包
3. **已修复** - 现在有 `requirements.txt` - 依赖关系已明确
4. **已修复** - 入口点通过包安装可用，也可直接运行 `src/startmyagent/examples/` 中的脚本
5. **已修复** - 移除了硬编码的 `sys.path.insert()` 调用，使用标准包导入

**学习项目的特定模式:**
- 代码按课程章节组织 (`chapters/chapter1`, `chapters/chapter3`)
- 提示词存储为 Markdown 文件，与代码放在一起
- 示例驱动的结构，包含 `examples/` 目录

## 反模式 (本项目)
*未找到明确的反模式注释。* 但是:

**结构性问题:**
1. **已修复** - 现在是标准的 Python 包 - 可通过 `import startmyagent` 导入
2. **已修复** - 移除了硬编码路径操作 - 使用标准包导入
3. **空的 `project/` 目录** - 只包含指南的 README（保持不变）
4. **混合内容类型** - 代码、笔记和提示词在同一层次结构中（未改变）
5. **已修复** - 添加了 `tests/` 目录和 pytest 配置

**代码问题 (探索发现):**
- `src/startmyagent/chapters/chapter3/transformer.py` - 关键bug: `super.__init__()` 应为 `super().__init__()` (第28行)
- `src/startmyagent/examples/basic_agent_usage.py` - 错误导入: `from chapters.chapter1.system_prompt` 应为 `from startmyagent.chapters.chapter1...` (第113行)
- `src/startmyagent/chapters/chapter3/transformer.py` - 缺少构造函数参数: `MultiHeadAttention()` 和 `PositionWiseFeedForward()` 需要参数 (第139-140行)
- `tests/conftest.py` - 反模式: 使用 `sys.path.insert()` 而非正确的包安装

## 独特风格
**教育项目的模式:**
- 基于章节的组织方式，而非基于功能/模块
- 示例脚本使用 `if __name__ == "__main__":` 块作为入口点
- 中文 Markdown 笔记与英文代码并存
- 根目录有虚拟环境 (`.venv/`) 但无依赖清单

## 常用命令
```bash
# 运行主要演示
python src/startmyagent/examples/basic_agent_usage.py

# 运行本地 LLM 演示  
python src/startmyagent/examples/local_llm_demo.py

# 运行 transformer/BPE 演示
python src/startmyagent/examples/transformer_bpe_demo.py

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 检查 git 状态 (尚未提交)
git status
```

## 注意事项
**这是一个学习代码库**，不是生产代码:
- 代码质量反映教育目的
- 缺少: 测试、CI/CD、打包、依赖管理
- 结构遵循课程安排而非软件工程最佳实践
- `project/` 目录是课程设计工作的模板

**如需用作正式项目:**
1. **已修复** - 将代码移动到 `src/` 目录
2. **已修复** - 添加 `pyproject.toml` 或 `setup.py`
3. **已修复** - 从 `.venv` 创建 `requirements.txt`
4. **已修复** - 添加 `tests/` 目录和 pytest 配置
5. **已修复** - 移除硬编码的 `sys.path.insert()` 调用

**探索发现的关键问题:**
- **入口点**: 示例放在 `src/startmyagent/examples/` (非标准位置)，缺少根目录 `main.py`
- **依赖**: `modelscope` 需要 `numpy`, `addict`, `transformers` (已在 pyproject.toml 添加)
- **测试**: `tests/conftest.py` 仍使用 `sys.path.insert()` 反模式
- **代码错误**: `transformer.py` 有多个关键语法错误需修复