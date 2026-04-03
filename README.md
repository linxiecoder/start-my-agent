# Start My Agent - AI代理与大型语言模型学习项目

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
</p>

## 📖 项目简介

Start My Agent 是一个专注于AI代理（AI Agents）和大型语言模型（LLM）的Python学习项目。本项目通过实践代码示例，帮助开发者理解和掌握以下核心概念：

- **AI代理架构**：如何构建能够感知、规划、执行和学习的智能代理
- **大模型集成**：如何与OpenAI兼容API及本地LLM进行交互
- **Transformer原理**：从零实现Transformer模型的核心组件
- **词元化技术**：实现和理解Byte Pair Encoding（BPE）算法
- **工具调用**：代理如何利用外部工具（天气查询、网络搜索等）完成任务

## ✨ 功能特性

- 🚀 **多章节渐进式学习**：从简单代理到复杂模型实现
- 🔧 **工具调用示例**：集成天气查询、旅游景点搜索等实际工具
- 🤖 **本地LLM支持**：支持使用ModelScope加载本地大模型
- 🧠 **Transformer实现**：从零实现Transformer模型核心组件
- 📚 **模块化设计**：清晰的目录结构和可复用的工具类
- 🔌 **开放API兼容**：支持任何OpenAI兼容的API服务

## 📁 项目结构

```
start-my-agent/
├── learning/                   # 学习笔记与文档
│   ├── chapter1/               # 第一章学习文档
│   │   └── chapter1_guide.md   # 基础AI代理指南
│   ├── chapter3/               # 第三章学习文档
│   │   └── chapter3_guide.md   # LLM与Transformer指南
│   └── notes/                  # 个人学习笔记（可自行添加）
├── practice/                   # 练习代码
│   ├── chapters/               # 章节代码
│   │   ├── chapter1/           # 第一章：基础AI代理
│   │   │   ├── system_prompt.py    # 旅行助手代理实现
│   │   │   └── __init__.py
│   │   ├── chapter3/           # 第三章：LLM与Transformer
│   │   │   ├── use_llm.py          # 本地LLM调用示例
│   │   │   ├── exercise_for_llm.py # LLM进阶练习
│   │   │   ├── transformer.py      # Transformer模型实现
│   │   │   ├── byte_pair_encoding.py # BPE算法实现
│   │   │   ├── prompt/             # 提示词模板
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── common/                 # 公共模块
│   │   ├── util/               # 工具类
│   │   │   ├── markdown_reader.py  # Markdown文件读取器
│   │   │   └── __init__.py
│   │   ├── config/             # 配置文件目录
│   │   └── __init__.py
│   └── examples/               # 使用示例
│       ├── basic_agent_usage.py    # 基础代理示例
│       ├── local_llm_demo.py       # 本地LLM示例
│       ├── transformer_bpe_demo.py # Transformer与BPE示例
│       └── README.md               # 示例说明
├── project/                    # 课程设计项目（完整应用）
│   └── README.md               # 项目说明（待完善）
├── requirements.txt            # Python依赖包列表
├── .env.example                # 环境变量示例（建议复制为.env）
└── README.md                   # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器
- （可选）支持CUDA的GPU用于本地模型推理

### 安装步骤

1. **克隆项目**
   ```bash
    git clone https://github.com/linxiecoder/start-my-agent.git
    cd start-my-agent
   ```

2. **安装依赖**

   推荐使用虚拟环境（可选但建议）：
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

   安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

   如果不存在`requirements.txt`，请手动安装以下包：
   ```bash
   pip install openai>=1.0.0 requests>=2.28.0 tavily-python>=0.1.0 torch>=2.0.0 modelscope>=1.9.0
   ```

   **GPU支持**：如需GPU加速本地模型推理，请安装CUDA版本的PyTorch：
   ```bash
   # 根据CUDA版本选择，示例为CUDA 11.8
   pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cu118
   ```

   **可选依赖**：项目中的开发依赖（如pytest）可根据需要安装。

3. **配置环境变量**
   创建`.env`文件并添加以下配置：
   ```env
   # OpenAI兼容API配置（示例使用DeepSeek API）
   API_KEY=your-api-key-here
   BASE_URL=https://api.deepseek.com
   MODEL_ID=deepseek-chat
   
   # Tavily搜索API（用于旅游景点搜索）
   TAVILY_API_KEY=your-tavily-api-key
   ```

## 📖 使用指南

### 第一章：基础AI代理

运行旅行助手代理示例：

```bash
cd practice/chapters/chapter1
python system_prompt.py
```

该示例演示了一个完整的AI代理工作流程：
1. 接收用户请求（如"查询北京天气并推荐景点"）
2. 使用Thought-Action格式进行规划
3. 调用工具获取天气信息
4. 根据天气搜索推荐景点
5. 返回最终答案

### 第三章：LLM与Transformer

#### 使用本地LLM
```bash
cd practice/chapters/chapter3
python use_llm.py
```

#### 运行Transformer实现
```bash
cd practice/chapters/chapter3
python transformer.py
```

#### 体验BPE算法
```bash
cd practice/chapters/chapter3
python byte_pair_encoding.py
```

## ⚙️ 配置说明

### API密钥获取

1. **OpenAI兼容API**：
   - 注册DeepSeek、OpenAI或其他兼容服务
   - 获取API密钥并配置到`.env`文件

2. **Tavily搜索API**：
   - 访问[Tavily官网](https://tavily.com/)注册
   - 获取API密钥用于网络搜索功能

3. **本地模型配置**：
   - 项目默认使用Qwen3-0.6B模型
    - 可修改`practice/chapters/chapter3/use_llm.py`中的`model_id`变量
   - 支持ModelScope上的所有开源模型

### 模型选择

项目支持多种模型配置：

1. **云端API模式**（Chapter1）：
   - 使用OpenAI兼容API
   - 响应速度快，无需本地资源

2. **本地模型模式**（Chapter3）：
   - 使用ModelScope加载本地模型
   - 需要GPU资源，但完全离线运行
   - 推荐：Qwen、ChatGLM、Baichuan等开源模型

## 🧪 示例代码

### 基础代理调用
```python
from practice.chapters.chapter1.system_prompt import AGENT_SYSTEM_PROMPT, OpenAICompatibleClient

# 初始化客户端
llm = OpenAICompatibleClient(
    model=MODEL_ID, 
    api_key=API_KEY, 
    base_url=BASE_URL
)

# 运行代理
response = llm.generate(
    prompt="查询上海天气并推荐景点",
    system_prompt=AGENT_SYSTEM_PROMPT
)
```

### 本地LLM调用
```python
from modelscope import AutoModelForCausalLM, AutoTokenizer

# 加载模型和分词器
model_id = "qwen/Qwen3-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to("cuda")

# 生成文本
inputs = tokenizer("你好，请介绍下你自己。", return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 🔧 工具函数

### 天气查询工具
```python
def get_weather(city: str) -> str:
    """
    查询指定城市的实时天气
    使用wttr.in免费API
    """
    # 实现代码见 practice/chapters/chapter1/system_prompt.py
    pass
```

### 旅游景点搜索
```python
def get_attractions(city: str, weather: str) -> str:
    """
    根据城市和天气搜索推荐景点
    使用Tavily搜索API
    """
    # 实现代码见 practice/chapters/chapter1/system_prompt.py
    pass
```

## 📚 学习路径

### 新手入门
1. 阅读第一章文档，理解AI代理的基本概念
2. 运行`system_prompt.py`，观察代理的思考过程
3. 尝试修改系统提示词，改变代理行为

### 进阶学习
1. 研究第三章的LLM本地调用
2. 理解Transformer模型的实现细节
3. 动手修改BPE算法，尝试不同的合并策略

### 项目扩展
1. 添加新的工具函数（股票查询、新闻搜索等）
2. 集成其他大模型API（Claude、Gemini等）
3. 实现更复杂的代理架构（ReAct、Chain of Thought）

## 🤝 贡献指南

我们欢迎任何形式的贡献！请遵循以下步骤：

1. **Fork项目**
2. **创建特性分支** (`git checkout -b feature/amazing-feature`)
3. **提交更改** (`git commit -m 'Add some amazing feature'`)
4. **推送到分支** (`git push origin feature/amazing-feature`)
5. **开启Pull Request**

### 贡献规范
- 代码遵循PEP 8规范
- 添加适当的注释和文档
- 为新功能添加测试用例
- 更新相关文档和示例

## 📄 许可证与版权声明

### 项目来源
本项目基于以下资源进行学习、扩展和修改：

1. **主要参考项目**: [DataWhale China 的 hello-agents 项目](https://github.com/datawhalechina/hello-agents)
2. **课程资料**: 参考了相关的公开AI课程资料和学习资源
3. **代码实现**: 在理解原理的基础上进行了代码重构、优化和扩展

### 版权声明
- 原始代码和概念版权归 DataWhale China 及相关课程提供方所有
- 本项目的重构、扩展和修改内容版权归 [linxiecoder](https://github.com/linxiecoder) 所有

### 开源协议
本项目采用 **MIT 许可证** - 查看 [LICENSE](LICENSE) 文件了解详情。

### 使用说明
1. 本项目主要用于学习目的，展示了AI代理和LLM的核心概念
2. 请遵守原项目的许可证要求
3. 欢迎基于本项目进行进一步的学习和研究

## 🙏 致谢

- 感谢 [DataWhale China](https://github.com/datawhalechina) 提供的原始 [hello-agents 项目](https://github.com/datawhalechina/hello-agents)
- 感谢所有开源AI模型和框架的贡献者
- 感谢[Tavily](https://tavily.com/)提供免费的搜索API
- 感谢[ModelScope](https://modelscope.cn/)提供丰富的模型资源
- 感谢所有为项目提交Issue和PR的开发者

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/linxiecoder/start-my-agent/issues)
- 发送邮件至：linxiecoder@yeah.net

---

⭐ **如果这个项目对你有帮助，请给它一个Star！** ⭐

<p align="center">
  <b>持续更新中...</b>
</p>