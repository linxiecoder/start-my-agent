import ast
from typing import List

from click import prompt

from src.startmyagent.chapters.chapter4.llm_client import HelloAgentsLLM

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。
问题:{question}

请严格按照以下格式输出你的计划，```python与```作为前后缀是必要的：
```python
["步骤1","步骤2","步骤3",...]
```
"""

EXECUTOR_PROMPT_TEMPLATE = """
你是一个顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题：
{question}

# 完整计划：
{plan}

# 历史步骤与结果：
{history}

# 当前步骤：
{current_step}

请仅输出针对“当前步骤”的回答：

"""


class Panner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def plan(self, question: str) -> List[str]:
        """
        根据用户问题生成一个行动计划
        :param question:
        :return:
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages) or ""

        if not response_text:
            print("错误：返回无结果")

        print(f"计划已生成：{response_text}")

        try:
            # 找到```python和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用ast.literal_eval来安全执行字符串，转为Python List列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except {ValueError, SyntaxError, IndexError} as e:
            print(f"错误：解析计划报错：{e}")
            print(f"原始计划为：{response_text}")
            return []
        except Exception as e:
            print(f"错误：解析计划报错，未知错误：{e}")
            print(f"原始计划为：{response_text}")
            return []


class Executor:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def execute(self, question: str, plan: List[str]) -> str:
        """
        根据计划，逐步执行并解决问题。
        :param question:
        :param plan:
        :return:
        """
        history = ""  # 用于存储历史步骤和结果的字符串
        print("\n---正在执行计划----")

        for i, step in enumerate(plan):
            print(f"正在执行步骤{i + 1}/{len(plan)}：{step}")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(question=question, plan=plan, history=history if history else "无",
                                                     current_step=i)

            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages) or ""
            history += f"步骤{i + 1}：{step}\n结果：{response_text}\n\n"
            print(f"步骤{i + 1}执行完成，模型响应为{response_text}")

        # 循环结束，最后一步的响应就是最终答案
        final_answer = response_text
        return final_answer


class PlanAndSolveAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.executor = Executor(llm_client)
        self.planner = Panner(llm_client)

    def run(self, question:str):
        print(f"问题：{question}")

        plan = self.planner.plan(question)

        if not plan:
            print(f"错误：任务终止，无法生成有效行动计划")

        final_answer = self.executor.execute(question, plan)
        print(f"最终答案{final_answer}")

if __name__ == "__main__":
    llm_client = HelloAgentsLLM()
    agent = PlanAndSolveAgent(llm_client)
    agent.run("一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？")