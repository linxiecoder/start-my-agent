# 第三章：LLM原理与Transformer实现

## 概述

本章深入探讨大型语言模型（LLM）的核心技术，包括：
- **本地LLM调用**：使用ModelScope加载和运行开源大模型
- **Transformer架构**：从零实现Transformer模型的关键组件
- **词元化技术**：实现Byte Pair Encoding（BPE）算法

通过实践这些底层技术，您将深入理解现代LLM的工作原理。

## 目录结构

```
chapters/chapter3/
├── use_llm.py              # 基础LLM调用示例
├── exercise_for_llm.py     # LLM进阶练习（参数调优）
├── transformer.py          # Transformer模型实现
├── byte_pair_encoding.py   # BPE算法实现
├── prompt/                 # 提示词模板目录
│   ├── system_prompt.md    # 系统提示词模板
│   └── user_prompt.md      # 用户提示词模板
└── __init__.py
```

## 1. 本地LLM调用

### 基础调用 (`use_llm.py`)

```python
import torch.cuda
from modelscope import AutoModelForCausalLM, AutoTokenizer

# 1. 指定模型ID
model_id = 'qwen/Qwen3-0.6B'  # 注意是小写 qwen

# 2. 设置设备，优先使用GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device:{device}")

# 3. 加载分词器
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# 4. 加载模型
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to(device)
```

#### 核心流程

1. **模型选择**：支持ModelScope上的所有开源模型
2. **设备检测**：自动检测GPU可用性，优先使用CUDA加速
3. **安全加载**：使用`trust_remote_code=True`处理自定义模型代码
4. **对话模板**：使用分词器的`apply_chat_template`方法格式化输入

#### 生成配置

```python
# 基础生成（贪婪解码）
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512  # 控制生成长度
)

# 进阶生成（带采样参数）
generated_ids = model.generate(
    model_inputs.input_ids,
    max_new_tokens=512,
    do_sample=True,      # 启用采样
    temperature=0.7,     # 控制随机性（0.0-1.0）
    top_p=0.9,           # 核采样（累积概率阈值）
    repetition_penalty=1.1  # 重复惩罚
)
```

### 进阶练习 (`exercise_for_llm.py`)

在基础调用上增加了：

1. **模块化导入**：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "common"))
from markdown_reader import MarkdownReader
```

2. **参数调优**：
   - `temperature=0.7`：适度的创造性
   - `top_p=0.9`：限制采样范围，提高一致性
   - `repetition_penalty=1.1`：轻微抑制重复内容

3. **Markdown集成**：
   - 演示如何从Markdown文件读取提示词
   - 为提示工程提供结构化支持

## 2. Transformer模型实现

### 架构概览

`transformer.py` 实现了Transformer的核心组件：

```python
# 主要组件
1. PositionalEncoding      # 位置编码
2. MultiHeadAttention     # 多头注意力
3. PositionwiseFeedForward # 前馈网络
4. TransformerEncoderLayer # 编码器层
5. TransformerEncoder      # 编码器堆栈
6. TransformerDecoderLayer # 解码器层
7. TransformerDecoder      # 解码器堆栈
8. Transformer             # 完整模型
```

### 关键实现细节

#### 位置编码 (PositionalEncoding)

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # 正弦/余弦位置编码公式
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * 
                           (-math.log(10000.0) / d_model))
        
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)  # 偶数维度
        pe[:, 1::2] = torch.cos(position * div_term)  # 奇数维度
        
        self.register_buffer('pe', pe.unsqueeze(0))
```

**数学原理**：
- 使用不同频率的正弦和余弦函数
- 每个位置有唯一的编码向量
- 支持模型理解序列中token的相对位置

#### 多头注意力 (MultiHeadAttention)

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # 每个头的维度
        
        # 线性变换层
        self.W_q = nn.Linear(d_model, d_model)  # 查询
        self.W_k = nn.Linear(d_model, d_model)  # 键
        self.W_v = nn.Linear(d_model, d_model)  # 值
        self.W_o = nn.Linear(d_model, d_model)  # 输出
        
        self.dropout = nn.Dropout(dropout)
```

**注意力计算流程**：
1. **线性投影**：将输入分别投影到Q、K、V空间
2. **分割头**：将投影后的张量分割成多个头
3. **缩放点积注意力**：计算注意力分数
4. **合并头**：将多个头的输出合并
5. **输出投影**：线性变换得到最终输出

#### 前馈网络 (PositionwiseFeedForward)

```python
class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)     # 扩展维度
        self.fc2 = nn.Linear(d_ff, d_model)     # 压缩维度
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()             # 激活函数
```

**设计特点**：
- **位置独立**：每个位置独立处理（因此称为"positionwise"）
- **维度扩展**：先扩展到更高维度（通常4倍），再压缩回原维度
- **非线性激活**：使用ReLU引入非线性

### 完整Transformer架构

```python
class Transformer(nn.Module):
    def __init__(self, 
                 src_vocab_size: int,
                 tgt_vocab_size: int,
                 d_model: int = 512,
                 num_heads: int = 8,
                 num_encoder_layers: int = 6,
                 num_decoder_layers: int = 6,
                 d_ff: int = 2048,
                 dropout: float = 0.1,
                 max_len: int = 5000):
        super().__init__()
        
        # 词嵌入
        self.src_embedding = nn.Embedding(src_vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, d_model)
        
        # 位置编码
        self.positional_encoding = PositionalEncoding(d_model, dropout, max_len)
        
        # 编码器
        self.encoder = TransformerEncoder(d_model, num_heads, 
                                         num_encoder_layers, d_ff, dropout)
        
        # 解码器
        self.decoder = TransformerDecoder(d_model, num_heads,
                                         num_decoder_layers, d_ff, dropout)
        
        # 输出层
        self.fc_out = nn.Linear(d_model, tgt_vocab_size)
        
        # 初始化参数
        self._init_parameters()
```

## 3. Byte Pair Encoding (BPE) 算法

### 算法原理

BPE是一种数据压缩算法，被广泛应用于LLM的词元化（tokenization）。基本思想是：

1. **初始化**：将文本分割为字符级别的词元
2. **统计频率**：统计所有相邻词元对的频率
3. **合并高频对**：将频率最高的词元对合并为新词元
4. **重复**：重复步骤2-3，直到达到预定合并次数或词表大小

### 实现详解 (`byte_pair_encoding.py`)

#### 初始化词表

```python
# 准备语料库，每个词末加上</w>表示结束，并切分好字符
vocab = {
    'h u g </w>': 1, 
    'p u g </w>': 1, 
    'p u n </w>': 1, 
    'b u n </w>': 1
}
```

**关键细节**：
- `</w>` 标记词尾，帮助模型识别词边界
- 空格分隔的字符表示初始词元化状态

#### 统计函数

```python
def get_stats(vocab):
    """
    统计词元对频率
    :param vocab: 当前词表 {词元串: 频率}
    :return: 词元对频率字典
    """
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[symbols[i], symbols[i + 1]] += freq
    return pairs
```

#### 合并函数

```python
def merge_vocab(pair, v_in):
    """
    合并词元对
    :param pair: 要合并的词元对，如 ('u', 'g')
    :param v_in: 输入词表
    :return: 合并后的新词表
    """
    v_out = {}
    bigram = re.escape(' '.join(pair))  # 转义特殊字符
    p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    
    for word in v_in:
        w_out = p.sub(''.join(pair), word)  # 合并匹配的词元对
        v_out[w_out] = v_in[word]
    
    return v_out
```

**正则表达式解析**：
- `(?<!\S)`：确保前面不是非空白字符（词边界）
- `bigram`：要合并的词元对（如 "u g"）
- `(?!\S)`：确保后面不是非空白字符（词边界）

#### 主循环

```python
num_merges = 4  # 设置合并次数

for i in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    
    best = max(pairs, key=pairs.get)  # 找到频率最高的词元对
    vocab = merge_vocab(best, vocab)  # 合并
    
    print(f"第{i + 1}次合并: {best} -> {''.join(best)}")
    print(f"新词表（部分）: {list(vocab.keys())}")
```

### 运行示例

```
初始词表: ['h u g </w>', 'p u g </w>', 'p u n </w>', 'b u n </w>']

第1次合并: ('u', 'g') -> ug
新词表: ['h ug </w>', 'p ug </w>', 'p u n </w>', 'b u n </w>']

第2次合并: ('u', 'n') -> un
新词表: ['h ug </w>', 'p ug </w>', 'p un </w>', 'b un </w>']

第3次合并: ('p', 'ug') -> pug
新词表: ['h ug </w>', 'pug </w>', 'p un </w>', 'b un </w>']

第4次合并: ('p', 'un') -> pun
新词表: ['h ug </w>', 'pug </w>', 'pun </w>', 'b un </w>']
```

## 4. 提示词模板系统

### 目录结构

```
prompt/
├── system_prompt.md    # 系统提示词模板
└── user_prompt.md      # 用户提示词模板
```

### 设计理念

1. **分离关注点**：系统提示词定义角色和行为，用户提示词定义具体任务
2. **模板化**：支持变量替换和动态生成
3. **可维护性**：将提示词从代码中分离，便于修改和版本控制

### 使用示例

```python
# 读取系统提示词模板
system_prompt_template = """
你是一个{role}。你的任务是{task}。

# 行为准则：
{guidelines}

# 输出格式：
{format}
"""

# 动态填充
system_prompt = system_prompt_template.format(
    role="编程助手",
    task="帮助用户解决编程问题",
    guidelines="1. 提供准确的代码示例\n2. 解释关键概念",
    format="先解释原理，再提供代码"
)
```

## 5. 配置与运行

### 环境准备

```bash
# 安装依赖
pip install torch modelscope

# 验证安装
python -c "import torch; print(f'PyTorch版本: {torch.__version__}')"
python -c "import modelscope; print(f'ModelScope版本: {modelscope.__version__}')"
```

### 运行示例

```bash
# 运行基础LLM示例
python use_llm.py

# 运行进阶LLM练习
python exercise_for_llm.py

# 运行Transformer实现（查看结构）
python transformer.py

# 运行BPE算法演示
python byte_pair_encoding.py
```

### GPU配置

如果拥有NVIDIA GPU：

```bash
# 安装CUDA版本的PyTorch（根据CUDA版本选择）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 验证CUDA可用性
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
```

## 6. 模型选择指南

### 推荐模型

| 模型 | 大小 | 推荐用途 | 备注 |
|------|------|----------|------|
| Qwen3-0.6B | 0.6B | 学习测试 | 轻量级，推理速度快 |
| Qwen1.5-0.5B | 0.5B | 入门体验 | 更小，资源要求低 |
| Qwen2.5-7B | 7B | 生产测试 | 能力更强，需要更多资源 |
| ChatGLM3-6B | 6B | 中文任务 | 中文优化，适合本地部署 |

### 切换模型

修改 `use_llm.py` 中的 `model_id`：

```python
# 使用不同模型
# model_id = "qwen/Qwen3-0.6B"  # 默认
# model_id = "Qwen/Qwen1.5-0.5B-Chat"  # 历史版本
# model_id = "ZhipuAI/glm-4-9b-chat"   # 智谱AI
# model_id = "baichuan-inc/Baichuan2-7B-Chat"  # 百川
```

## 7. 进阶学习建议

### 理解Transformer

1. **阅读原始论文**："Attention Is All You Need" (2017)
2. **可视化工具**：使用TensorFlow Playground或类似工具理解注意力机制
3. **逐行调试**：在调试器中逐步执行transformer.py，观察张量形状变化

### 扩展BPE算法

1. **实现完整分词器**：添加特殊词元处理、未知词处理
2. **添加词汇表保存/加载**：支持训练后保存BPE词表
3. **性能优化**：使用更高效的数据结构统计词元对频率

### 提示工程实践

1. **A/B测试**：比较不同提示词模板的效果
2. **少样本学习**：在提示词中添加示例，演示期望的输出格式
3. **思维链**：设计引导模型逐步思考的提示词

## 8. 常见问题

### Q: 加载模型时内存不足
**A**: 尝试以下方法：
1. 使用更小的模型（如0.5B而非7B）
2. 启用CPU模式（自动回退）
3. 使用量化版本（如4bit量化）
4. 分批处理输入，减少同时处理的数据量

### Q: 生成结果不理想
**A**: 调整生成参数：
1. 降低temperature（如0.3）减少随机性
2. 调整top_p（如0.8）限制采样范围
3. 增加repetition_penalty（如1.2）减少重复
4. 修改max_new_tokens控制生成长度

### Q: 注意力机制不理解
**A**: 推荐学习资源：
1. [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)（可视化教程）
2. [Transformer直观解释](https://towardsdatascience.com/transformers-explained-visually-part-1-overview-of-functionality-95a6dd460452)
3. [注意力机制数学推导](https://lilianweng.github.io/posts/2018-06-24-attention/)

## 9. 学习成果检查

完成本章学习后，您应该能够：

✅ **理解LLM调用流程**：从模型加载到文本生成的完整过程  
✅ **实现Transformer组件**：位置编码、注意力机制、前馈网络  
✅ **掌握BPE算法**：理解词元化的基本原理和实现  
✅ **配置提示词系统**：设计可维护的提示词模板  
✅ **调试模型问题**：识别和解决常见的内存、性能问题  
✅ **扩展模型功能**：添加新组件或修改现有架构  

## 下一步行动

1. **动手实验**：尝试不同的模型和参数组合
2. **代码研究**：深入阅读ModelScope和PyTorch源码
3. **项目应用**：将学到的技术应用到实际项目中
4. **社区贡献**：在GitHub上分享您的改进或教程

---

*文档最后更新：2025年4月3日*