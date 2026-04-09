import os
import re

import requests
from openai import OpenAI
from tavily import TavilyClient

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


def get_attractions(city: str, weather: str) -> str:
    """
    根据天气和城市查找推荐景点，调用Tavily Search API
    :param city:
    :param weather:
    :return:
    """
    # 1.从环境变量获取API秘钥
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "错误：未配置TAVILY_API_KEY环境变量"
    # 2.初始化Tavily客户端
    tavily = TavilyClient(api_key)
    # 3.构造精确查询
    query = f"'{city}'在'{weather}'天气下最值得去的旅游景点推荐及理由"

    # 4.调用API，include_answer=true会返回一个综合性的回答
    response = tavily.search(query=query, search_depth="basic", include_answer=True)

    # 5.判断结果
    if response.get("answer"):
        return response.get("answer")

    formatted_result = []
    for result in response.get("results", []):
        formatted_result.append(f"-{result['title']}:{result['content']}")

    if not formatted_result:
        return "抱歉，没有找到相关的旅游景点推荐"

    return "根据搜索，为您返回如下推荐结果：\n" + "\n".join(formatted_result)


def get_weather(city: str) -> str:
    """
    通过调用wttr.in API查询指定城市的实时天气信息
    :param city:
    :return:
    """
    url = f'http://wttr.in/{city}?format=j1'

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # 提取天气信息
    current_condition = data['current_condition'][0]
    weather_desc = current_condition['weatherDesc'][0]['value']
    temp_c = current_condition['temp_C']

    return f'{city}当前天气：{weather_desc}，气温{temp_c}摄氏度'


available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attractions
}


class OpenAICompatibleClient:
    """
    一个用于调用任何兼容OpenAI接口的LLM服务的客户端
    """

    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, prompt: str, system_prompt: str) -> str:
        """
        调用大模型API来生成回答
        :param prompt:
        :param system_prompt:
        :return:
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = self.client.chat.completions.create(model=self.model, messages=messages, stream=False)
        answer = response.choices[0].message.content
        print("大模型回答成功")
        return answer


# 1.配置LLM客户端
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")
MODEL_ID = os.environ.get("MODEL_ID")

if __name__ == "__main__":
    llm = OpenAICompatibleClient(model=MODEL_ID, api_key=API_KEY, base_url=BASE_URL)

    # 2.初始化
    user_prompt = "你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点"
    prompt_history = [f"用户请求：{user_prompt}"]
    print(f"用户输入：{user_prompt}\n" + "=" * 40)
    # 3.执行主循环
    for i in range(5):
        print(f"---循环{i+1}\n")
        # 3.1构建Prompt
        full_prompt = "\n".join(prompt_history)

        # 3.2调用LLM思考
        llm_output = llm.generate(full_prompt,system_prompt=AGENT_SYSTEM_PROMPT)
        # 模型可能输出多余的Thought-Action，需要阶段
        match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
        if match:
            truncated  = match.group(1).strip()
            if truncated!=llm_output.strip():
                llm_output = truncated
                print("已经截断多余的Thought-Action对")
        print("模型已经输出：\n{}".format(llm_output))
        prompt_history.append(llm_output)

        # 3.3解析规划并立即行动
        action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
        if not action_match:
            observation = "错误：未能解析到Action字段。请确保你的回复严格遵循‘Thought：...Action：...’的格式"
            observation_str = f"Observation:{observation}"
            print(f"{observation_str}\n" + "=" * 40)
            prompt_history.append(observation_str)
            continue
        action_str = action_match.group(1).strip()

        if action_str.startswith("Finish"):
            final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
            print(f"任务完成，最终答案{final_answer}\n" + "=" * 40)
            break

        tool_name = re.search(r"(\w+)\(", action_str).group(1)
        args_str = re.search(r"\((.*)\)", action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误：未定义的工具‘{tool_name}’"

        # 3.4 记录观察结果
        observation_str = f"Observation:{observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)