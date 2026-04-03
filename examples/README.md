# 项目示例代码

本目录包含Hello Agents项目的使用示例，帮助您快速上手和理解项目功能。

## 📁 示例文件

| 文件名 | 描述 | 难度 | 运行时间 |
|--------|------|------|----------|
| [basic_agent_usage.py](./basic_agent_usage.py) | 基础AI代理使用示例 | 初级 | 1-2分钟 |
| [local_llm_demo.py](./local_llm_demo.py) | 本地LLM调用演示 | 中级 | 3-5分钟（首次运行需下载模型） |
| [transformer_bpe_demo.py](./transformer_bpe_demo.py) | Transformer与BPE算法演示 | 高级 | 1-2分钟 |

## 🚀 快速开始

### 环境准备

```bash
# 进入项目根目录
cd /path/to/hello-agents

# 安装基础依赖
pip install openai requests tavily-python

# 如需运行本地LLM示例，还需安装
pip install torch modelscope
```

### 配置环境变量

创建 `.env` 文件（在项目根目录）：

```env
# OpenAI兼容API配置
API_KEY=your-api-key-here
BASE_URL=https://api.deepseek.com
MODEL_ID=deepseek-chat

# Tavily搜索API（用于旅游景点搜索）
TAVILY_API_KEY=your-tavily-api-key
```

## 📖 示例详解

### 1. 基础AI代理示例 (`basic_agent_usage.py`)

**功能**：
- 演示第一章旅行助手代理的完整工作流程
- 展示代理的思考→行动→观察循环
- 提供多个查询示例
- 演示工具函数的直接调用

**运行**：
```bash
cd /path/to/hello-agents
python examples/basic_agent_usage.py
```

**输出示例**：
```
🔍 用户查询: 你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点
🔄 第1轮思考...
🤖 模型输出:
Thought: 用户需要查询北京天气，然后根据天气推荐景点。我需要先调用get_weather获取天气信息。
Action: get_weather(city="北京")
...
✅ 任务完成!
📋 最终答案:
北京当前天气晴朗，气温25°C。推荐您参观故宫...
```

### 2. 本地LLM演示 (`local_llm_demo.py`)

**功能**：
- 检查运行环境（Python、PyTorch、ModelScope）
- 演示本地模型加载和推理
- 比较不同生成参数的效果
- 提供模型选择和内存管理建议

**运行**：
```bash
# 首次运行会下载模型（约1-2GB）
python examples/local_llm_demo.py
```

**注意**：
- 需要稳定的网络连接下载模型
- 需要至少4GB可用内存（CPU）或2GB显存（GPU）
- 首次运行时间较长，后续运行会使用缓存

**输出示例**：
```
🔍 检查环境...
   ✅ Python版本: 3.10.0
   ✅ PyTorch版本: 2.0.0
   🚀 CUDA可用: NVIDIA GeForce RTX 3060
📦 使用模型: qwen/Qwen3-0.6B
💬 模型回答:
你好！我是Qwen，一个由阿里云开发的大语言模型...
```

### 3. Transformer与BPE演示 (`transformer_bpe_demo.py`)

**功能**：
- 演示BPE词元化算法的工作原理
- 讲解Transformer核心组件（注意力、位置编码等）
- 展示完整Transformer架构
- 提供动手练习建议

**运行**：
```bash
python examples/transformer_bpe_demo.py
```

**输出示例**：
```
🔤 BPE（Byte Pair Encoding）算法演示
原始词表（字符级别）:
  'h u g </w>'
  'p u g </w>'
  'p u n </w>'
  'b u n </w>'
📊 词元对频率统计:
  ('u', 'g') -> 2次
  ('u', 'n') -> 2次
  ('h', 'u') -> 1次
🔄 模拟BPE合并过程:
  第1次合并:
    最高频词元对: ('u', 'g') (出现2次)
    合并为: 'ug'
    新词表: ['h ug </w>', 'p ug </w>', 'p u n </w>', 'b u n </w>']
```

## 🔧 自定义示例

### 修改查询内容

编辑 `basic_agent_usage.py` 中的查询列表：

```python
# 第XX行附近
queries = [
    "你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点",
    "我想去上海旅游，能告诉我上海的天气和推荐景点吗？",
    # 添加您自己的查询
    "广州有什么好玩的景点？天气怎么样？"
]
```

### 切换模型

编辑 `local_llm_demo.py` 中的模型ID：

```python
# 第XX行附近
model_id = "qwen/Qwen3-0.6B"  # 默认
# 可选其他模型:
# model_id = "Qwen/Qwen1.5-0.5B-Chat"  # 更小的模型
# model_id = "qwen/Qwen2.5-1.5B"       # 稍大的模型
```

### 调整生成参数

在 `local_llm_demo.py` 中修改生成参数：

```python
# 第XX行附近
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=200,    # 生成长度
    do_sample=True,        # 启用采样
    temperature=0.7,       # 创造性（0.0-1.0）
    top_p=0.9,             # 核采样阈值
    repetition_penalty=1.1 # 重复惩罚
)
```

## 🧪 测试说明

### 依赖检查

每个示例都包含环境检查功能，会自动检测：

1. **Python版本**：需要3.8+
2. **必要包**：torch, modelscope等
3. **API配置**：环境变量是否设置
4. **硬件资源**：GPU可用性、内存大小

### 错误处理

示例包含完善的错误处理：

- 缺少依赖时的清晰提示
- API调用失败时的优雅降级
- 内存不足时的建议措施
- 网络超时的重试机制

## 📚 学习路径

建议按以下顺序运行示例：

1. **初学者**：先运行 `basic_agent_usage.py`，了解AI代理的基本概念
2. **进阶学习**：运行 `local_llm_demo.py`，掌握本地模型调用
3. **深入理解**：运行 `transformer_bpe_demo.py`，学习底层原理

## 🆘 常见问题

### Q: 运行时报错"ModuleNotFoundError"
**A**: 请安装缺失的包：
```bash
pip install 缺失的包名
```

### Q: 本地LLM示例下载模型太慢
**A**: 
1. 使用国内镜像：`pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/`
2. 手动下载模型到缓存目录
3. 使用更小的模型（如0.5B版本）

### Q: API调用失败
**A**:
1. 检查网络连接
2. 验证API密钥是否正确
3. 确认API服务是否可用
4. 查看错误信息中的具体原因

### Q: 内存不足
**A**:
1. 使用更小的模型
2. 减少生成长度（max_new_tokens）
3. 使用CPU模式
4. 分批处理数据

## 📈 性能优化建议

### 对于CPU运行：
```python
# 使用float32而非float16
model = AutoModelForCausalLM.from_pretrained(
    model_id, 
    torch_dtype=torch.float32  # CPU上float16可能更慢
).to("cpu")
```

### 对于GPU运行：
```python
# 使用float16节省显存
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16  # 半精度，节省显存
).to("cuda")
```

### 批处理优化：
```python
# 同时处理多个输入
batch_prompts = ["问题1", "问题2", "问题3"]
inputs = tokenizer(batch_prompts, return_tensors="pt", padding=True).to(device)
outputs = model.generate(**inputs)
```

## 🤝 贡献示例

欢迎贡献新的示例！请遵循以下格式：

1. **文件命名**：`描述性名称_demo.py`
2. **文档头**：包含功能描述和使用方法
3. **错误处理**：完善的异常捕获和用户提示
4. **注释**：关键代码添加中文注释
5. **测试**：确保示例能正常运行

## 📄 许可证

示例代码遵循项目主许可证（MIT）。

---

*最后更新：2025年4月3日*