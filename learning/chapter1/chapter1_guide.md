# 第一章：基础AI代理实现指南

## 概述

本章实现了一个完整的旅行助手AI代理，能够理解用户请求、规划行动、调用外部工具并生成最终答案。该代理采用了经典的Thought-Action模式，展示了AI代理的基本工作原理。

## 核心组件

### 1. 系统提示词 (AGENT_SYSTEM_PROMPT)

位于 `system_prompt.py` 中的系统提示词定义了代理的行为规范：

```python
AGENT_SYSTEM_PROMPT = """
你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具：
- `get_weather(city: str)`:查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`: 根据城市和天气搜索推荐的旅游景点。

# 输出格式：
你的每次回复必须严格遵循以下格式，包含一对Thought和Action：

Thought: [你的思考过程和下一步机会]
Action: [你要执行的具体行动]

Action的格式必须是以下之一：
1.调用工具：function_name(arg_name="arg_value")
2.结束任务：Finish[最终答案]

# 重要提示：
- 每次只输出一对Thought和Action
- Action必须在同一行，不要换行
- 当收集到足够的信息可以回答用户问题时，必须使用Action：Finish[最终答案]格式结束

请开始吧！
"""
```

**关键设计要点：**
- **结构化输出**：强制代理按照Thought-Action格式思考，便于程序解析
- **工具定义**：明确声明可用的工具及其参数
- **终止条件**：定义明确的结束信号（Finish[最终答案]）

### 2. 工具函数实现

#### 天气查询工具 (`get_weather`)

```python
def get_weather(city: str) -> str:
    """
    通过调用wttr.in API查询指定城市的实时天气信息
    :param city: 城市名称
    :return: 天气描述字符串
    """
```

**实现特点：**
- 使用免费的 `wttr.in` API
- 返回格式化的天气信息（天气描述+温度）
- 异常处理确保API调用失败时的优雅降级

#### 旅游景点搜索工具 (`get_attractions`)

```python
def get_attractions(city: str, weather: str) -> str:
    """
    根据天气和城市查找推荐景点，调用Tavily Search API
    :param city: 城市名称
    :param weather: 天气描述
    :return: 景点推荐结果
"""
```

**实现特点：**
- 集成Tavily搜索API进行智能搜索
- 根据天气条件优化搜索关键词
- 支持两种结果格式：AI生成的摘要或原始搜索结果列表

### 3. OpenAI兼容客户端 (`OpenAICompatibleClient`)

```python
class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端
    """
```

**设计优势：**
- **通用性**：支持任何OpenAI兼容API（DeepSeek、OpenAI、本地部署等）
- **配置灵活**：通过环境变量动态配置API端点、密钥和模型
- **简单接口**：统一的`generate`方法，接受prompt和system_prompt

## 工作流程

### 主循环架构

```python
# 1. 初始化
user_prompt = "你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点"
prompt_history = [f"用户请求：{user_prompt}"]

# 2. 执行主循环（最多5轮）
for i in range(5):
    # 构建完整prompt
    full_prompt = "\n".join(prompt_history)
    
    # 调用LLM生成思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    
    # 解析并执行Action
    if Action是工具调用:
        执行对应工具
        记录Observation
    elif Action是Finish:
        输出最终答案
        结束循环
```

### 数据流示例

```
用户请求：查询北京天气并推荐景点
↓
Thought: 用户需要查询北京天气，然后根据天气推荐景点。我需要先调用get_weather获取天气信息。
Action: get_weather(city="北京")
↓
Observation: 北京当前天气：晴朗，气温25摄氏度
↓
Thought: 现在有了天气信息，可以调用get_attraction搜索适合晴朗天气的北京景点。
Action: get_attraction(city="北京", weather="晴朗")
↓
Observation: 根据搜索，为您返回如下推荐结果：-故宫：明清两代皇家宫殿...
↓
Thought: 我已经收集了所有必要信息，可以给出最终答案了。
Action: Finish[北京当前天气晴朗，气温25°C。推荐您参观故宫，这是明清两代的皇家宫殿...]
```

## 关键技术细节

### 1. 输出解析与清理

由于LLM可能生成不符合格式的文本，代码实现了智能截断：

```python
# 使用正则表达式匹配第一个完整的Thought-Action对
match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', 
                  llm_output, re.DOTALL)
if match:
    truncated = match.group(1).strip()
    llm_output = truncated
```

### 2. Action解析与执行

```python
# 解析Action类型
if action_str.startswith("Finish"):
    # 提取最终答案
    final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
else:
    # 解析工具调用
    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))
    
    # 执行工具
    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
```

### 3. 工具注册机制

```python
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attractions
}
```

这种设计使得添加新工具变得非常简单。

## 配置指南

### 环境变量设置

创建 `.env` 文件：

```env
# OpenAI兼容API配置
API_KEY=your-api-key-here
BASE_URL=https://api.deepseek.com  # 或您的API端点
MODEL_ID=deepseek-chat

# Tavily搜索API
TAVILY_API_KEY=your-tavily-api-key
```

### API服务选择

1. **DeepSeek API**（推荐）：
   - 注册：https://platform.deepseek.com/
   - 免费额度：足够学习和测试使用

2. **OpenAI API**：
   - 注册：https://platform.openai.com/
   - 需要付费，但稳定可靠

3. **本地部署**：
   - 使用OpenAI兼容的本地服务（如LocalAI、Ollama）
   - 将BASE_URL设置为本地端点

## 运行与测试

### 基本运行

```bash
cd chapters/chapter1
python system_prompt.py
```

### 自定义查询

修改 `system_prompt.py` 中的用户请求：

```python
# 第129行附近
user_prompt = "你好，请帮我查询下今天上海的天气，然后根据天气推荐一个合适的旅游景点"
```

### 调试模式

要查看详细的思考过程，可以调整打印语句：

```python
# 在第147行后添加
print(f"第{i+1}轮思考完成")
print(f"历史记录长度：{len(prompt_history)}")
```

## 扩展与定制

### 添加新工具

1. **实现工具函数**：
```python
def get_hotel_info(city: str, budget: str) -> str:
    """根据城市和预算查询酒店信息"""
    # 实现逻辑
```

2. **注册工具**：
```python
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attractions,
    "get_hotel": get_hotel_info  # 新增
}
```

3. **更新系统提示词**：
在 `AGENT_SYSTEM_PROMPT` 的可用工具部分添加：
```
- `get_hotel(city: str, budget: str)`: 根据城市和预算查询酒店信息
```

### 修改代理行为

1. **调整思考深度**：
```python
# 修改主循环次数（第133行）
for i in range(10):  # 增加为10轮
```

2. **改变输出格式**：
修改系统提示词中的输出格式部分，例如添加更多结构要求。

### 错误处理增强

当前实现已包含基本错误处理，可进一步扩展：

```python
# 在工具函数中添加重试机制
def get_weather_with_retry(city: str, max_retries: int = 3) -> str:
    for attempt in range(max_retries):
        try:
            return get_weather(city)
        except Exception as e:
            if attempt == max_retries - 1:
                return f"错误：查询天气失败 - {str(e)}"
            time.sleep(1)  # 等待后重试
```

## 常见问题与解决

### 1. API调用失败
- **症状**：程序报错或返回错误信息
- **解决**：
  - 检查网络连接
  - 验证API密钥是否正确
  - 确认API端点可访问

### 2. 解析错误
- **症状**：无法正确解析LLM的输出
- **解决**：
  - 检查系统提示词的格式要求
  - 添加更严格的输出验证
  - 在解析前清理LLM输出中的多余字符

### 3. 无限循环
- **症状**：代理无法正确结束
- **解决**：
  - 检查终止条件逻辑
  - 增加最大循环次数限制
  - 添加超时机制

## 学习要点

通过本章的学习，您应该掌握：

1. **AI代理的基本架构**：感知→思考→行动→观察的循环
2. **工具调用模式**：如何让代理使用外部工具
3. **结构化提示工程**：设计可解析的系统提示词
4. **API集成技巧**：安全、可靠地集成第三方服务
5. **错误处理策略**：确保代理在各种情况下的鲁棒性

## 下一步

完成本章学习后，建议：

1. **动手实践**：添加至少一个新工具并测试
2. **代码研究**：深入理解每个函数的工作原理
3. **性能优化**：尝试改进错误处理和解析逻辑
4. **继续学习**：进入第三章学习LLM和Transformer原理

---

*文档最后更新：2025年4月3日*