#!/usr/bin/env python3
"""


基础AI代理使用示例

本示例演示如何使用第一章实现的旅行助手代理。
展示了代理的完整工作流程：思考→行动→观察→完成。

使用方法：
1. 配置环境变量（API_KEY, BASE_URL, MODEL_ID, TAVILY_API_KEY）
2. 运行: python practice/examples/basic_agent_usage.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入第一章的代理
from chapters.chapter1.system_prompt import (
    AGENT_SYSTEM_PROMPT,
    OpenAICompatibleClient,
    available_tools
)

def setup_environment():
    """配置环境变量"""
    env_vars = {
        "API_KEY": os.environ.get("API_KEY"),
        "BASE_URL": os.environ.get("BASE_URL"),
        "MODEL_ID": os.environ.get("MODEL_ID", "deepseek-chat"),
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY")
    }
    
    # 检查必要环境变量
    missing = [key for key, value in env_vars.items() if not value]
    if missing:
        print("❌ 缺少必要环境变量:")
        for key in missing:
            print(f"  - {key}")
        print("\n请创建 .env 文件并设置这些变量，或通过命令行设置。")
        print("示例 .env 文件内容:")
        print("""
API_KEY=your-api-key-here
BASE_URL=https://api.deepseek.com
MODEL_ID=deepseek-chat
TAVILY_API_KEY=your-tavily-api-key
        """)
        sys.exit(1)
    
    return env_vars

def run_basic_query(llm_client, query):
    """运行基础查询示例"""
    print(f"🔍 用户查询: {query}")
    print("=" * 60)
    
    # 初始化历史记录
    prompt_history = [f"用户请求：{query}"]
    
    # 主循环（最多5轮）
    for i in range(5):
        print(f"\n🔄 第{i+1}轮思考...")
        
        # 构建完整prompt
        full_prompt = "\n".join(prompt_history)
        
        # 调用LLM
        llm_output = llm_client.generate(full_prompt, AGENT_SYSTEM_PROMPT)
        print(f"🤖 模型输出:\n{llm_output}")
        
        # 添加到历史记录
        prompt_history.append(llm_output)
        
        # 检查是否为完成信号
        if "Finish[" in llm_output:
            print("\n✅ 任务完成!")
            # 提取最终答案
            import re
            match = re.search(r"Finish\[(.*)\]", llm_output, re.DOTALL)
            if match:
                final_answer = match.group(1).strip()
                print(f"📋 最终答案:\n{final_answer}")
            break
        
        print("-" * 40)

def run_multiple_queries(llm_client):
    """运行多个查询示例"""
    queries = [
        "你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点",
        "我想去上海旅游，能告诉我上海的天气和推荐景点吗？",
        "杭州的天气怎么样？有什么推荐游玩的地方？"
    ]
    
    print("🚀 运行多个查询示例")
    print("=" * 60)
    
    for idx, query in enumerate(queries, 1):
        print(f"\n📝 示例 {idx}/{len(queries)}")
        run_basic_query(llm_client, query)
        if idx < len(queries):
            print("\n" + "="*60 + "\n")

def demonstrate_tool_usage():
    """演示工具函数的直接调用"""
    print("🛠️  演示工具函数直接调用")
    print("=" * 60)
    
    # 导入工具函数
    from chapters.chapter1.system_prompt import get_weather, get_attractions
    
    # 演示天气查询
    print("\n1. 直接调用天气查询工具:")
    weather_result = get_weather("北京")
    print(f"   北京天气: {weather_result}")
    
    # 演示景点搜索
    print("\n2. 直接调用景点搜索工具:")
    attraction_result = get_attractions("北京", "晴朗")
    print(f"   北京晴朗天气推荐:\n   {attraction_result[:200]}...")

def main():
    """主函数"""
    print("🤖 AI代理使用示例")
    print("=" * 60)
    
    # 1. 环境设置
    print("1. 检查环境配置...")
    env_vars = setup_environment()
    print("   ✅ 环境配置检查通过")
    
    # 2. 初始化LLM客户端
    print("\n2. 初始化LLM客户端...")
    llm = OpenAICompatibleClient(
        model=env_vars["MODEL_ID"],
        api_key=env_vars["API_KEY"],
        base_url=env_vars["BASE_URL"]
    )
    print("   ✅ LLM客户端初始化完成")
    
    # 3. 运行示例
    print("\n3. 开始运行示例...")
    
    # 3.1 基础查询
    run_basic_query(llm, "你好，请帮我查询下今天北京的天气，然后根据天气推荐一个合适的旅游景点")
    
    # 3.2 多个查询
    print("\n" + "="*60)
    run_multiple_queries(llm)
    
    # 3.3 工具函数演示
    print("\n" + "="*60)
    demonstrate_tool_usage()
    
    print("\n" + "="*60)
    print("🎉 所有示例运行完成！")
    print("\n💡 提示:")
    print("1. 要修改查询内容，请编辑此脚本中的queries列表")
    print("2. 要添加新工具，请参考 chapters/chapter1/system_prompt.py")
    print("3. 要自定义代理行为，请修改系统提示词")

if __name__ == "__main__":
    main()