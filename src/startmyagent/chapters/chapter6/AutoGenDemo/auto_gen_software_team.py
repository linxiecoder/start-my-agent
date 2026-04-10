"""
AutoGen 软件开发团队 - 支持动态回退的协作流程

本示例展示如何实现动态回退机制：
- 工程师代码需要返回给产品经理重新审核
- 代码审查意见需要回退给工程师修改
- 测试发现 bug 需要回退给工程师修复

【新增】对话质量监控机制：
- 循环检测：检测重复的发言者序列或内容
- 主题漂移检测：检测对话是否偏离原始目标
- 响应质量评估：检测重复或低质量响应
- 干预机制：异常时自动提醒或终止

使用 SelectorGroupChat + 自定义选择函数实现动态跳转
"""

import asyncio
import os
import traceback
from typing import List, Optional

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import BaseChatMessage
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

# 导入对话质量监控模块
from conversation_monitor import (
    ConversationMonitor,
    AlertLevel,
    MonitorResult,
    create_monitor,
)

# 加载 .env 文件中的环境变量
load_dotenv()


# ============================================================================
# 动态回退控制消息定义
# ============================================================================


class ControlTags:
    """控制指令标签"""

    # 回退到产品经理 (需求变更/确认)
    PM_REVIEW = "[需产品经理确认]"

    # 回退到工程师 (代码修改)
    ENGINEER_REVISION = "[需要修改]"

    # 回退到审查员 (重新审查)
    REVIEWER_REVIEW = "[重新审查]"

    # 回退到 QA 测试 (测试失败)
    QA_RETEST = "[需QA测试]"

    # 终止
    FINISH = "[完成]"


# 控制消息 -> 目标智能体映射
CONTROL_TO_TARGET = {
    ControlTags.PM_REVIEW: "ProductManager",
    ControlTags.ENGINEER_REVISION: "Engineer",
    ControlTags.REVIEWER_REVIEW: "CodeReviewer",
    ControlTags.QA_RETEST: "QAEngineer",
    ControlTags.FINISH: None,  # None 表示终止
}


# ============================================================================
# 模型客户端创建
# ============================================================================


def create_openai_model_client() -> OpenAIChatCompletionClient:
    """创建并配置 OpenAI 模型客户端"""
    # DeepSeek 模型信息配置
    from autogen_ext.models.openai._model_info import ModelInfo

    model_info = ModelInfo(
        family="deepseek",
        function_calling=True,
        json_output=False,
        multiple_system_messages=True,
        vision=False,
        structured_output=False,
    )

    return OpenAIChatCompletionClient(
        model=os.getenv("LLM_MODEL_ID"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        model_info=model_info,
    )


# ============================================================================
# 智能体创建 - 嵌入动态回退控制指令
# ============================================================================


def create_product_manager(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建产品经理智能体"""
    system_message = """
你是一个经验丰富的产品经理，专门负责软件产品的需求分析和项目规划。

你的核心职责包括：
1. **需求分析**：深入理解用户需求，识别核心功能和边界条件
2. **技术规划**：基于需求制定清晰的技术实现路径
3. **风险评估**：识别潜在的技术风险和用户体验问题
4. **协调沟通**：与工程师和其他团队成员进行有效沟通

当接到开发任务时，请按以下结构进行分析：
1. 需求理解与分析
2. 功能模块划分
3. 技术选型与建议
4. 实现优先级划分
5. 验收标准与定义

当工程师请求你确认需求细节时，请明确回答。如果需要变更需求，请清晰说明变更内容。
分析完成后说"请工程师开始实现"。
"""
    return AssistantAgent(
        name="ProductManager", model_client=model_client, system_message=system_message
    )


def create_engineer(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建工程师智能体 - 支持动态回退"""
    system_message = """
你是一位资深的软件工程师，擅长 Python 开发和 Web 应用构建。

你的技术专长包括：
1. **Python 编程**：熟练掌握 Python 语法和最佳实践
2. **Web 开发**：精通 Streamlit、Flask、Django 等框架
3. **API 集成**：有丰富的第三方 API 集成经验
4. **错误处理**：注重代码的健壮性和异常处理

【动态回退机制】当遇到以下情况时，必须使用特定指令标记：

1. **需求有歧义或遗漏** → 说 "[需产品经理确认] + 具体问题描述"
   示例："[需产品经理确认]未明确说明用户登录方式是本地还是第三方？"

2. **代码发现严重问题需确认** → 说 "[需产品经理确认] + 问题描述"
   示例："[需产品经理确认]当前设计无法满足高并发需求，是否调整？"

3. **代码已完成** → 说 "请代码审查员检查"

4. **代码需要修改** → 说 "[需要修改] + 修改说明"
   示例："[需要修改]需修复登录验证逻辑的边界情况"
"""
    return AssistantAgent(
        name="Engineer", model_client=model_client, system_message=system_message
    )


def create_code_reviewer(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建代码审查员智能体"""
    system_message = """
你是一位经验丰富的代码审查专家，专注于代码质量和最佳实践。

你的审查重点包括：
1. **代码质量**：检查代码的可读性、可维护性和性能
2. **安全性**：识别潜在的安全漏洞和风险点
3. **最佳实践**：确保代码遵循行业标准和最佳实践
4. **错误处理**：验证异常处理的完整性和合理性

【动态回退机制】审查完成后：

1. **代码通过** → 说 "代码审查通过，请QA工程师测试"

2. **需要修改** → 说 "[需要修改] + 具体修改建议"
   示例："[需要修改]建议将硬编码的 URL 配置为环境变量"

3. **严重问题需讨论** → 说 "[需产品经理确认] + 问题描述"
   示例："[需产品经理确认]安全审查发现的设计缺陷需要重新讨论"
"""
    return AssistantAgent(
        name="CodeReviewer", model_client=model_client, system_message=system_message
    )


def create_qa_engineer(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """创建 QA 工程师智能体 - 自动化测试"""
    system_message = """
你是一位专业的质量保证 (QA) 工程师，擅长自动化测试和 Bug 定位。

你的核心职责：
1. **自动化测试**：编写和执行测试用例，验证功能正确性
2. **Bug 定位**：快速定位问题根因，提供复现步骤
3. **回归测试**：确保修复不引入新问题
4. **测试报告**：提供清晰的测试结果和改进建议

【动态回退机制】测试完成后：

1. **测试通过** → 说 "测试通过，请用户代理验收"

2. **测试失败** → 说 "[需要修改] + 复现步骤和修复建议"
   示例："[需要修改]价格格式化错误：输入 '50000' 期望 '$50,000' " \
       "实际为 '50000'，需添加千分位格式化"

3. **严重问题需确认** → 说 "[需产品经理确认] + 问题描述"
   示例："[需产品经理确认]需求中未明确负数价格的处理方式"

4. **需要重新审查** → 说 "[重新审查] + 审查建议"
   示例："[重新审查]代码逻辑变更较大，建议重新审查"

测试策略：
- 优先测试核心功能（价格显示、刷新、数据解析）
- 验证边界情况（API 失败、无网络、超时）
- 检查用户友好性（加载状态、错误提示）
"""
    return AssistantAgent(
        name="QAEngineer", model_client=model_client, system_message=system_message
    )


def create_user_proxy() -> UserProxyAgent:
    """创建用户代理智能体"""
    return UserProxyAgent(
        name="UserProxy",
        description="""
用户代理，负责以下职责：
1. 代表用户提出开发需求
2. 执行最终的代码实现
3. 验证功能是否符合预期
4. 提供用户反馈和建议

【动态回退机制】测试完成后：

1. **功能正常** → 回复 "[完成]"

2. **发现问题需修复** → 说 "[需要修改] + 问题描述"
   示例："[需要修改]k线图显示异常，需检查数据格式化逻辑"

3. **需求变更** → 说 "[需产品经理确认] + 变更内容"
   示例："[需产品经理确认]需要添加多币种支持"
""",
    )


# ============================================================================
# 动态选择函数 - 核心回退机制实现
# ============================================================================

# 定义角色名称列表 (与 participants 顺序对应)
ROLE_NAMES = ["ProductManager", "Engineer", "CodeReviewer", "QAEngineer", "UserProxy"]


# ===== 对话质量监控器实例 =====
# 全局监控器，在 run_software_development_team 中初始化
_conversation_monitor: Optional[ConversationMonitor] = None


def _on_monitor_warning(result: MonitorResult) -> None:
    """监控警告回调 - 检测到潜在问题时调用"""
    print(f"\n⚠️ 对话质量警告: {result.reason}")
    print("   建议操作: ", result.recommended_action)


def _on_monitor_critical(result: MonitorResult) -> None:
    """监控严重问题回调 - 检测到严重问题时调用"""
    print(f"\n🚨 对话异常: {result.reason}")


async def select_speaker(messages: List[BaseChatMessage]) -> str | None:
    """
    根据消息历史动态选择下一个发言者

    实现逻辑:
    1. 获取最后一条消息
    2. 检查是否包含控制标签
    3. 如果包含，返回目标角色名称
    4. 如果不包含，按照轮询顺序选择下一个

    【新增】对话质量监控:
    - 在每条消息后记录到监控器
    - 执行质量检查
    - 检测到异常时打印警告信息

    Args:
        messages: 对话历史消息列表

    Returns:
        下一个发言者的角色名称，或 None 表示终止
    """
    global _conversation_monitor

    # 1. 记录消息到监控器并检查
    if messages and _conversation_monitor:
        latest_message = messages[-1]
        _conversation_monitor.record(latest_message)

        # 执行质量检查
        check_result = _conversation_monitor.check()

        # 如果检测到问题，打印警告
        if check_result.needs_intervention():
            alert_icon = (
                "🚨" if check_result.alert_level == AlertLevel.CRITICAL else "⚠️"
            )
            print(f"\n{alert_icon} 质量监控: {check_result.reason}")

    # 2. 原有的控制标签检查
    if not messages:
        return ROLE_NAMES[0]

    last_message = messages[-1]
    content = last_message.content

    # 检查所有控制指令
    for control_tag, target_name in CONTROL_TO_TARGET.items():
        if control_tag in content:
            if target_name is None:
                # 终止信号
                print(f"\n🎯 检测到终止信号: {control_tag}")
                return None
            else:
                # 跳转到指定角色
                print(f"\n🔄 动态回退: → {target_name}")
                return target_name

    # 3. 默认轮询顺序 - 使用 source 属性
    current_name = getattr(last_message, "source", None)

    if current_name in ROLE_NAMES:
        current_idx = ROLE_NAMES.index(current_name)
        next_idx = (current_idx + 1) % len(ROLE_NAMES)
    else:
        next_idx = 0

    return ROLE_NAMES[next_idx]


# ============================================================================
# 团队创建
# ============================================================================


async def run_software_development_team():
    """运行支持动态回退的软件开发团队"""
    global _conversation_monitor

    print("🔧 正在初始化模型客户端...")
    model_client = create_openai_model_client()

    print("👥 正在创建智能体团队...")
    # 创建智能体
    product_manager = create_product_manager(model_client)
    engineer = create_engineer(model_client)
    code_reviewer = create_code_reviewer(model_client)
    qa_engineer = create_qa_engineer(model_client)
    user_proxy = create_user_proxy()

    # 构建参与者字典 (用于动态回退选择)
    participants_dict = {
        "ProductManager": product_manager,
        "Engineer": engineer,
        "CodeReviewer": code_reviewer,
        "QAEngineer": qa_engineer,
        "UserProxy": user_proxy,
    }

    # 创建终止条件
    termination = TextMentionTermination(ControlTags.FINISH)

    # ===== 初始化对话质量监控器 =====
    print("📊 正在初始化对话质量监控器...")
    initial_task = """
    我们需要开发一个比特币价格显示应用，具体要求如下：
    核心功能：
    - 实时显示比特币当前价格（USD）
    - 显示24小时价格变化趋势（涨跌幅和涨跌额）
    - 提供价格刷新功能
    技术要求：
    - 使用 Streamlit 框架创建 Web 应用
    """
    _conversation_monitor = create_monitor(
        max_turns=40,
        on_warning=_on_monitor_warning,
        on_critical=_on_monitor_critical,
    )
    _conversation_monitor.initialize(initial_task)

    # 创建 SelectorGroupChat 团队 (关键区别于 RoundRobin)
    # 注意: SelectorGroupChat 需要 model_client 参数
    team_chat = SelectorGroupChat(
        participants=[
            product_manager,
            engineer,
            code_reviewer,
            qa_engineer,
            user_proxy,
        ],
        model_client=model_client,  # 必须提供
        selector_func=select_speaker,
        termination_condition=termination,
        max_turns=40,  # 增加轮次限制以支持多次回退
    )

    # 定义开发任务
    task = """
    我们需要开发一个比特币价格显示应用，具体要求如下：

    核心功能：
    - 实时显示比特币当前价格（USD）
    - 显示24小时价格变化趋势（涨跌幅和涨跌额）
    - 提供价格刷新功能

    技术要求：
    - 使用 Streamlit 框架创建 Web 应用
    - 界面简洁美观，用户友好
    - 添加适当的错误处理和加载状态

    请团队协作完成这个任务，从需求分析到最终实现。

    注意：本需求可能有不确定之处，工程师可以请求产品经理确认。
    """

    # 执行团队协作
    print("🚀 启动 AutoGen 软件开发团队 (支持动态回退)...")
    print("=" * 60)
    print("📋 控制指令说明:")
    print(f"  - {ControlTags.PM_REVIEW}: 回退到产品经理确认")
    print(f"  - {ControlTags.ENGINEER_REVISION}: 回退到工程师修改")
    print(f"  - {ControlTags.REVIEWER_REVIEW}: 回退到审查员重新审查")
    print(f"  - {ControlTags.FINISH}: 终止流程")
    print("=" * 60)
    print("📊 对话质量监控: 已启用 (循环检测、漂移检测、质量评估)")
    print("=" * 60)

    results = await Console(team_chat.run_stream(task=task))

    print("\n" + "=" * 60)
    print("✅ 团队协作完成！")

    return results


# ============================================================================
# 主入口
# ============================================================================

if __name__ == "__main__":
    try:
        result = asyncio.run(run_software_development_team())
        print("\n📋 协作结果摘要:")
        print("- 参与智能体数量: 4个")
        status = "成功" if result else "需要进一步处理"
        print(f"- 任务完成状态: {status}")

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请检查 .env 文件中的配置是否正确")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        traceback.print_exc()
