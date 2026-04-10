import streamlit as st
import requests
import time
from datetime import datetime
import os

# ---------- 配置 ----------
# 从环境变量读取API端点，提高灵活性和安全性
API_URL = os.getenv('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3/simple/price')
REFRESH_INTERVAL = 30  # 自动刷新间隔（秒）
CACHE_TTL = 25  # 缓存时间，略小于刷新间隔，确保自动刷新时能获取新数据

# 定义User-Agent头，模拟浏览器请求
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# ---------- 辅助函数：数据获取模块 ----------
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def fetch_bitcoin_data():
    """
    从CoinGecko API获取比特币数据。
    返回: (成功标志, 数据或错误信息)
    """
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd',
        'include_24hr_change': 'true',
        'include_last_updated_at': 'true'
    }

    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        btc_data = data.get('bitcoin')
        if not btc_data:
            return False, "API返回的数据格式异常，缺少比特币数据"

        return True, btc_data

    except requests.exceptions.Timeout:
        return False, "请求超时，请检查网络连接"
    except requests.exceptions.ConnectionError:
        return False, "网络连接失败，请检查网络设置"
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            return False, "API调用过于频繁，请稍后再试"
        return False, f"HTTP错误: {e}"
    except (KeyError, ValueError) as e:
        return False, f"数据解析错误: {e}"
    except Exception as e:
        return False, f"未知错误: {e}"


# ---------- 辅助函数：核心计算模块 ----------
def calculate_change_data(btc_data):
    """
    根据API返回的数据，计算用于显示的信息。
    增加边缘情况检查，提高健壮性。
    """
    if not btc_data:
        return None

    current_price = btc_data.get('usd')
    change_percentage_24h = btc_data.get('usd_24h_change')
    last_updated_timestamp = btc_data.get('last_updated_at')

    if None in (current_price, change_percentage_24h):
        return None

    # 边缘情况：涨跌幅为-100%（理论上不可能，但增加检查）
    if change_percentage_24h == -100:
        return {
            'current_price': current_price,
            'change_percentage_24h': change_percentage_24h,
            'change_amount_24h': -current_price,  # 价格归零
            'last_updated': "未知",
            'note': "极端情况：24小时前价格未知"
        }

    # 正常情况计算
    try:
        price_24h_ago = current_price / (1 + change_percentage_24h / 100)
        change_amount_24h = current_price - price_24h_ago
    except ZeroDivisionError:
        # 虽然上面已经检查了-100的情况，这里再加一道保险
        return None

    # 格式化时间戳
    last_updated_str = "未知"
    if last_updated_timestamp:
        try:
            last_updated_str = datetime.fromtimestamp(last_updated_timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, OSError):
            last_updated_str = "时间格式错误"

    return {
        'current_price': current_price,
        'change_percentage_24h': change_percentage_24h,
        'change_amount_24h': change_amount_24h,
        'last_updated': last_updated_str,
        'note': None  # 正常情况无备注
    }


# ---------- 主应用 ----------
def main():
    st.set_page_config(
        page_title="Bitcoin Price Tracker",
        page_icon="₿",
        layout="centered"
    )

    st.title("₿ Bitcoin Price Tracker")
    st.caption("实时追踪比特币兑美元价格")

    # 初始化Session State
    if 'last_fetch_time' not in st.session_state:
        st.session_state.last_fetch_time = 0
    if 'force_refresh' not in st.session_state:
        st.session_state.force_refresh = False
    if 'last_data' not in st.session_state:
        st.session_state.last_data = None

    # ---------- 侧边栏控制区 ----------
    with st.sidebar:
        st.header("控制面板")

        # 手动刷新按钮
        if st.button("🔄 手动刷新数据", use_container_width=True, type="primary"):
            st.session_state.force_refresh = True
            # 清除缓存，确保获取新数据
            fetch_bitcoin_data.clear()
            st.rerun()

        st.divider()

        # 显示配置信息
        st.caption(f"自动刷新间隔: {REFRESH_INTERVAL} 秒")
        st.caption(f"缓存时间: {CACHE_TTL} 秒")
        st.caption("数据来源: CoinGecko API")

        # 显示环境信息（调试用，生产环境可注释掉）
        if st.checkbox("显示调试信息", False):
            st.write(f"API端点: {API_URL}")
            st.write(
                f"上次获取: {datetime.fromtimestamp(st.session_state.last_fetch_time).strftime('%H:%M:%S') if st.session_state.last_fetch_time else '从未'}")

    # ---------- 主显示区 ----------
    price_container = st.container()

    # 检查是否需要刷新数据
    current_time = time.time()
    need_refresh = False

    if st.session_state.force_refresh:
        need_refresh = True
    elif (current_time - st.session_state.last_fetch_time) > REFRESH_INTERVAL:
        need_refresh = True

    # 获取数据
    if need_refresh:
        with st.spinner("正在获取最新数据..."):
            success, data = fetch_bitcoin_data()

        if success:
            display_data = calculate_change_data(data)
            st.session_state.last_data = display_data
        else:
            # 获取失败，使用上次成功的数据（如果有）
            display_data = st.session_state.last_data
            # 显示错误信息
            st.error(f"⚠️ 获取数据失败: {data}")
            st.info("""
            可能的原因：
            1. 网络连接问题
            2. CoinGecko API暂时不可用
            3. 数据格式异常

            已显示上次成功获取的数据（如有），请检查网络后点击 **`手动刷新数据`** 按钮重试。
            """)

        # 更新状态
        st.session_state.last_fetch_time = current_time
        st.session_state.force_refresh = False
    else:
        # 使用上次的数据
        display_data = st.session_state.last_data

    # 在价格容器中显示数据
    with price_container:
        if display_data:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.metric(
                    label="**当前价格 (USD)**",
                    value=f"${display_data['current_price']:,.2f}",
                    delta=None
                )

            with col2:
                change_color = "inverse"
                delta_prefix = "+" if display_data['change_amount_24h'] >= 0 else ""

                st.metric(
                    label="**24小时变化**",
                    value="",
                    delta=f"{delta_prefix}{display_data['change_amount_24h']:+.2f} ({display_data['change_percentage_24h']:+.2f}%)",
                    delta_color=change_color
                )

            # 显示最后更新时间
            st.caption(f"最后更新: {display_data['last_updated']}")

            # 如果有备注（如极端情况），显示备注
            if display_data.get('note'):
                st.warning(display_data['note'])

            # 预留趋势图区域
            st.divider()
            with st.expander("📈 查看24小时价格趋势 (开发中)", expanded=False):
                st.info("""
                **趋势图表功能正在开发中...**

                *规划功能：*
                - 显示过去24小时的价格曲线图
                - 支持切换时间范围（7天，30天）
                - 图表可交互缩放
                """)

        elif not need_refresh and st.session_state.last_data is None:
            # 首次加载，还没有数据
            st.info("正在初始化应用，请稍候...")

    # ---------- 改进的自动刷新逻辑 ----------
    # 不再使用time.sleep阻塞线程，而是依赖Streamlit的自然重新运行
    # 同时提供视觉反馈，让用户知道何时会刷新

    if display_data:
        # 计算距离下次刷新的时间
        time_since_refresh = int(current_time - st.session_state.last_fetch_time)
        refresh_in = max(0, REFRESH_INTERVAL - time_since_refresh)

        # 创建进度条显示刷新进度
        progress = 1 - (refresh_in / REFRESH_INTERVAL)

        # 使用columns创建更美观的进度显示
        col_left, col_right = st.columns([4, 1])

        with col_left:
            st.progress(progress, text=f"自动刷新倒计时: {refresh_in}秒")

        with col_right:
            # 提供立即刷新的按钮
            if st.button("立即刷新", key="instant_refresh"):
                st.session_state.force_refresh = True
                fetch_bitcoin_data.clear()
                st.rerun()

    # 注意：我们移除了底部的time.sleep和st.rerun()逻辑
    # Streamlit会在以下情况下重新运行脚本：
    # 1. 用户与组件交互
    # 2. 浏览器标签页重新聚焦
    # 3. Streamlit的默认定期检查（约每200ms）
    # 这种设计避免了阻塞，同时保持了应用的响应性


# ---------- 程序入口 ----------
if __name__ == "__main__":
    main()