import re

from src.startmyagent.chapters.chapter4.llm_client import HelloAgentsLLM
from src.startmyagent.chapters.chapter4.Tools import search, ToolExecutor

# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调研外部工具的智能助手。
可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought:你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action:你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出答案。

现在请你解决以下问题:
Question:{question}
History:{history}
"""


class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def _parse_output(self, output: str):
        # 解析Thought（思考）
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", output, re.DOTALL)
        # 解析Action（行动）
        # 正则失效，是因为要用search方法，match只适合开头匹配
        action_match = re.search(r"Action:\s*(.*?)$", output, re.DOTALL)
        thought_str = thought_match.group(1).strip() if thought_match else None
        action_str = action_match.group(1).strip() if action_match else None
        return thought_str, action_str

    def _parse_action(self, action: str):
        match = re.match(r"(\w+)\[(.*)\]", action, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def run(self, question: str):
        """
        运行ReAct智能体来回答问题
        :param question: 用户问题
        :return: 最终答案/输出
        """
        self.history = []  # 每轮问答开始重置上下文
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"current_step:{current_step}")

            # 1.格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history=history_str)

            # 2.调用LLM进行思考
            messages = [{"role": "user", "content": prompt}]
            llm_output = self.llm_client.think(messages)
            if not llm_output:
                print(f"错误：LLM未能返回有效响应")
                break

            # 3.解析结果
            thought, action = self._parse_output(llm_output)
            if thought:
                print(f"思考：{thought}")

            if not action:
                print(f"错误：未能解析出有效地Action，流程终止。")
                break

            if action.startswith("Finish"):
                # 以Finish开头说明有最终答案
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"最终答案：{final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                print(f"错误：未能解析出有效地工具，流程跳过。")
                continue

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                print(f"错误：未能找到有效地工具{tool_name}")
            observation = tool_function(tool_input)
            if not observation:
                print(f"错误：工具调用无有效返回。")
            else:
                print(f"观察：{observation}")
                self.history.append(action)
                self.history.append(observation)

        print("当前已经循环超出最大步长，流程终止。")
        return None


if __name__ == "__main__":
    try:
        llmClient = HelloAgentsLLM()
        tool_executor = ToolExecutor()
        search_desc = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
        tool_executor.registerTool("Search", search_desc, search)
        reActAgent = ReActAgent(llmClient, tool_executor)
        responseText = reActAgent.run("华为最新手机型号及主要卖点（2026年）")

        if responseText:
            print()
            print(responseText)

    except Exception as e:
        print(e)
