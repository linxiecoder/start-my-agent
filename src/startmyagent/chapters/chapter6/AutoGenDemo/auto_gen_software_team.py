from autogen_ext.models.openai import OpenAIChatCompletionClient

def create_openai_model_client():
    """
    创建并配置OpenAI模型客户端
    :return:
    """
    return OpenAIChatCompletionClient()