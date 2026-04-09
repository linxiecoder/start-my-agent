import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

# 加载.env中的环境变量
load_dotenv()


class HelloAgentsLLM:
    """
    为教程中的Agent定制LLM客户端。
    用于调用任何兼容OpenAI接口的服务，并默认使用流式响应
    """

    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供则从环境变量加载
        :param model: 模型ID
        :param apiKey: 模型API KEY
        :param baseUrl: 模型URL
        :param timeout: 超时时间
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or os.getenv("LLM_TIMEOUT", 60)

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、模型API KEY，服务地址未提供或未在.env文件中定义")
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0):
        """
        调用大模型进行思考，返回其响应。
        :param messages:对话消息列表，每条包含Role和content
        :param temperature:采样温度，0表示稳定输出
        :return:模型返回的文本内容
        """
        print(f"正在调用{self.model}模型...")
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=temperature,
                                                           stream=True)
            # 处理流式响应
            print("大模型响应成功...")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)

        except Exception as e:
            print(f"大模型调用失败，{e}")
            return None


if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()

        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print()
            print(responseText)

    except Exception as e:
        print(e)
