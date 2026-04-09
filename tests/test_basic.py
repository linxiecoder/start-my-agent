"""
基础测试用例
"""
import os
import pytest


def test_import():
    """测试能否导入主要模块"""
    # 设置环境变量以避免导入时认证错误
    os.environ["API_KEY"] = "dummy"
    os.environ["BASE_URL"] = "https://api.deepseek.com"
    os.environ["MODEL_ID"] = "deepseek-chat"
    os.environ["TAVILY_API_KEY"] = "dummy"
    
    try:
        from startmyagent.chapters.chapter1.system_prompt import OpenAICompatibleClient
        from startmyagent.common.util.markdown_reader import MarkdownReader
        assert True
    except ImportError as e:
        pytest.fail(f"导入失败: {e}")


def test_markdown_reader():
    """测试MarkdownReader"""
    from startmyagent.common.util.markdown_reader import MarkdownReader
    
    reader = MarkdownReader()
    # 测试读取不存在的文件应返回空字符串
    result = reader.read("non_existent_file.md")
    assert result == ""


def test_client_initialization():
    """测试OpenAICompatibleClient类初始化"""
    # 设置环境变量以避免导入时认证错误
    os.environ["API_KEY"] = "dummy"
    os.environ["BASE_URL"] = "https://api.deepseek.com"
    os.environ["MODEL_ID"] = "deepseek-chat"
    os.environ["TAVILY_API_KEY"] = "dummy"
    
    from startmyagent.chapters.chapter1.system_prompt import OpenAICompatibleClient
    
    # 使用环境变量中的值初始化客户端
    client = OpenAICompatibleClient(
        model=os.environ["MODEL_ID"],
        api_key=os.environ["API_KEY"],
        base_url=os.environ["BASE_URL"]
    )
    assert client is not None
    assert hasattr(client, 'client')
    assert hasattr(client, 'model')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])