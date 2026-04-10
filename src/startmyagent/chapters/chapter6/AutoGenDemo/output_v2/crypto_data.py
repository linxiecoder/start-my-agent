# crypto_data.py
"""
比特币价格数据获取模块 - 安全增强版
"""
import requests
import time
from typing import Dict, Optional, Tuple
from datetime import datetime
from config import Config


class BitcoinDataFetcher:
    """比特币数据获取器 - 安全增强版"""

    def __init__(self):
        """初始化，使用配置中的超时时间"""
        self.timeout = Config.API_TIMEOUT
        self.last_fetch_time = None
        self.last_data = None

    @staticmethod
    def _format_timestamp(timestamp: int) -> str:
        """安全地格式化时间戳"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return "时间格式错误"

    @staticmethod
    def _calculate_change_amount(current_price: float,
                                 change_percent: float) -> float:
        """计算涨跌额"""
        try:
            return current_price * (change_percent / 100)
        except (TypeError, ZeroDivisionError):
            return 0.0

    def fetch_bitcoin_price(self) -> Tuple[Optional[Dict], Optional[str]]:
        """
        安全地从API获取比特币价格数据

        Returns:
            (data, error_message): 数据字典和错误信息
        """
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }

        try:
            # 使用配置中的API URL
            response = requests.get(
                Config.API_URL,
                params=params,
                timeout=self.timeout
            )

            # 检查HTTP状态码
            response.raise_for_status()

            # 安全解析JSON
            data = response.json()

            # 验证数据结构
            if not isinstance(data, dict) or 'bitcoin' not in data:
                return None, "API返回数据格式无效"

            btc_data = data['bitcoin']

            # 验证必需字段
            required_fields = ['usd', 'usd_24h_change', 'last_updated_at']
            for field in required_fields:
                if field not in btc_data:
                    return None, f"数据缺少必需字段: {field}"

            # 类型转换和验证
            try:
                current_price = float(btc_data['usd'])
                change_percent = float(btc_data['usd_24h_change'])
                last_updated = int(btc_data['last_updated_at'])
            except (ValueError, TypeError):
                return None, "数据格式转换错误"

            # 构建返回数据
            formatted_data = {
                'current_price': current_price,
                'price_change_24h': self._calculate_change_amount(current_price, change_percent),
                'price_change_percentage_24h': change_percent,
                'last_updated_timestamp': last_updated,
                'last_updated_readable': self._format_timestamp(last_updated)
            }

            # 更新状态
            self.last_fetch_time = time.time()
            self.last_data = formatted_data

            return formatted_data, None

        except requests.exceptions.Timeout:
            return None, "请求超时，请检查网络连接后重试"
        except requests.exceptions.ConnectionError:
            return None, "网络连接错误，请检查网络设置"
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "未知"
            return None, f"API服务异常 (状态码: {status_code})"
        except ValueError as e:
            return None, "数据解析失败，请稍后重试"
        except Exception as e:
            # 避免泄露内部错误信息
            return None, "系统暂时不可用，请稍后重试"


# 单例实例
data_fetcher = BitcoinDataFetcher()