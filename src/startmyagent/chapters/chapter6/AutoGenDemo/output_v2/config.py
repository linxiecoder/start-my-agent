# config.py
"""
应用配置模块
安全地管理配置参数
"""
import os
from typing import Optional


def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    安全获取环境变量

    Args:
        key: 环境变量名
        default: 默认值

    Returns:
        环境变量值或默认值
    """
    value = os.getenv(key)
    if value is None:
        if default is None:
            raise ValueError(f"环境变量 {key} 未设置且无默认值")
        return default
    return value


class Config:
    """应用配置"""

    # API配置 - 使用环境变量，支持未来更换数据源
    API_URL = get_env_var(
        'CRYPTO_API_URL',
        "https://api.coingecko.com/api/v3/simple/price"
    )

    # 超时时间（秒）
    API_TIMEOUT = int(get_env_var('API_TIMEOUT', '10'))

    # 刷新冷却时间（秒）- 防止频繁刷新
    REFRESH_COOLDOWN = int(get_env_var('REFRESH_COOLDOWN', '3'))