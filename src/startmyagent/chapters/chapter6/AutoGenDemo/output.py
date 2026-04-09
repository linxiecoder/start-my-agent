import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# 常量配置
API_URL = "https://api.coingecko.com/api/v3/coins/bitcoin"
HEADERS = {
    "User-Agent": "bitcoin-price-app/1.0"
}

def fetch_bitcoin_data():
    """
    从CoinGecko API获取比特币当前行情数据。
    返回:
        dict: 包含当前价格、24小时涨跌额、24小时涨跌幅及最后更新时间。
    异常:
        RuntimeError: 请求失败
        ValueError: 响应数据不完整或时间解析错误
    """
    try:
        response = requests.get(
            API_URL,
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            },
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"请求API失败: {e}")

    market_data = data.get("market_data", {})
    current_price = market_data.get("current_price", {}).get("usd")
    price_change_24h = market_data.get("price_change_24h_in_currency", {}).get("usd")
    price_change_percentage_24h = market_data.get("price_change_percentage_24h")
    last_updated_raw = data.get("last_updated")

    if not all([current_price, price_change_24h, price_change_percentage_24h, last_updated_raw]):
        raise ValueError("API返回数据不完整")

    try:
        last_updated = datetime.fromisoformat(last_updated_raw.rstrip("Z"))
    except Exception as e:
        raise ValueError(f"时间格式解析错误: {e}")

    return {
        "current_price": current_price,
        "price_change_24h": price_change_24h,
        "price_change_percentage_24h": price_change_percentage_24h,
        "last_updated": last_updated
    }

def fetch_price_chart_data():
    """
    获取过去24小时内的比特币价格历史数据，用于趋势图展示。
    返回:
        pd.DataFrame 或 None: 包含"time"和"price"两列的DataFrame，失败返回None。
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    try:
        resp = requests.get(
            url,
            params={
                "vs_currency": "usd",
                "days": "1",
                "interval": "hourly"
            },
            headers=HEADERS,
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        prices = data.get("prices", [])
        if not prices:
            return None
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df[["time", "price"]]
    except Exception as e:
        st.warning(f"价格趋势图加载异常: {e}")
        return None

def display_price_info(data):
    """
    在Streamlit页面展示当前价格及24小时涨跌信息。
    """
    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader("当前价格:")
        st.markdown(f"<h2 style='color:#FF9900;'>${data['current_price']:,.2f}</h2>", unsafe_allow_html=True)
        st.caption(f"数据最后更新时间：{data['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}（UTC）")
    with col2:
        price_change = data['price_change_24h']
        price_change_pct = data['price_change_percentage_24h']
        is_up = price_change > 0
        color = "green" if is_up else "red"
        arrow = "▲" if is_up else "▼"
        st.subheader("24小时走势:")
        st.markdown(
            f"<h3 style='color:{color};'>{arrow} {price_change:+,.2f} USD ({price_change_pct:+.2f}%)</h3>",
            unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="比特币价格监控", layout="centered")
    st.title("🚀 实时比特币价格监控")
    st.write("显示比特币当前价格及24小时内涨跌趋势（美元）")

    refresh = st.button("刷新价格")

    # 初始化状态
    if "btc_data" not in st.session_state:
        st.session_state.btc_data = None
        st.session_state.error = None
        st.session_state.loading = False

    # 首次加载或刷新请求数据
    if refresh or st.session_state.btc_data is None:
        st.session_state.loading = True

    if st.session_state.loading:
        with st.spinner("加载中，请稍候..."):
            try:
                btc_data = fetch_bitcoin_data()
                st.session_state.btc_data = btc_data
                st.session_state.error = None
            except (RuntimeError, ValueError) as e:
                st.session_state.error = str(e)
                st.session_state.btc_data = None
            finally:
                st.session_state.loading = False

    # 根据状态展示信息
    if st.session_state.error:
        st.error(f"数据获取失败：{st.session_state.error}")
    elif st.session_state.btc_data:
        display_price_info(st.session_state.btc_data)

        with st.spinner("获取24小时价格趋势..."):
            df_chart = fetch_price_chart_data()
            if df_chart is not None:
                # 未来可考虑用Plotly丰富交互体验
                st.line_chart(df_chart.set_index('time')['price'])
            else:
                st.info("趋势图加载失败，显示当前价格和涨跌统计。")

if __name__ == "__main__":
    main()