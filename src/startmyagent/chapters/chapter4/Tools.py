import os

import json
from typing import Dict, Any, Callable

from dotenv import load_dotenv
from serpapi import SerpApiClient

# 加载.env中的环境变量
load_dotenv()


def search(query: str):
    """
    一个基于SerpApi的实战网页搜索引擎工具
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息
    :param query: 查询信息、条件
    :return: 查询结果
    """
    print(f"正在执行[SerpApi]网页搜索：{query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：PERSAPI_API_KEY未在.env文件中配置"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gi": "cn",
            "hi": "zh-cn"
        }

        client = SerpApiClient(params)
        results = client.get_dict()
        results1 = json.dumps(results, indent=4)
        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有找到直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i + 1}]{res.get('title', '')}\n{res.get('snippet', '')}" for i, res in
                enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于‘{query}’的信息。"

    except Exception as e:
        return f"搜索时发生错误：{e}"


class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: Callable):
        if name in self.tools:
            print(f"警告：工具{name}已经存在，即将被覆盖")

        self.tools[name] = {"description": description, "func": func}
        print(f"工具{name}注册成功")

    def getTool(self, name: str) -> Callable:
        return self.tools.get(name).get("func")

    def getAvailableTools(self) -> str:
        return "\n".join(
            [f"-{name}:{info['description']}"
             for name, info in self.tools.items()]
        )
