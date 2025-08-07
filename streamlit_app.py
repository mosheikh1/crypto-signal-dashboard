import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="centered")

st.title("📈 Crypto Futures Signal Dashboard")
st.markdown("Real-time BUY/SELL signals using RSI & MACD indicators.")

# Sidebar selection
symbol = st.sidebar.selectbox("Select Crypto Pair", ["BTC-USD", "ETH-USD", "SOL-USD"])
interval = st.sidebar.selectbox("Select Timeframe", ["1h", "4h", "1d"])
st.sidebar.markdown("⚠️ Data from Yahoo Finance")

# Data fetch function
@st.cache_data(ttl=300)
def get_data(symbol, interval):
    if interval == "1h":
        return yf.download(tickers=symbol, period="7d", interval="1h")
    elif interval == "4h":
        return yf.download(tickers=symbol, period="30d", interval="4h")
    else:
        return yf.download(tickers=symbol, period="90d", interval="1d")

data = get_data(symbol, interval)

# --- Safe Check for 'Close' column ---
if 'Close' not in data.columns:
    st.error("❌ 'Close' column not found in the data.")
else:
    close_data = data['Close']

    # Make sure there's enough valid data
    if close_data.isnull().sum() > 0:
        st.warning("⚠️ Some missing values detected in price data. Attempting to clean...")
        close_data = close_data.fillna(method='ffill')

    if close_data.dropna().shape[0] < 50:
        st.error("❌ Not enough data to calculate indicators. Try another timeframe.")
    else:
        # Add indicators
        data['RSI'] = ta.momentum.RSIIndicator(close=close_data).rsi()
        macd = ta.trend.MACD(close=close_data)
        data['MACD'] = macd.macd()
        data['Signal'] = macd.macd_signal()
        data.dropna(inplace=True)

        if data.empty:
            st.error("❌ No valid data after indicator calculation.")
        else:
            latest = data.iloc[-1]

            def generate_signal(row):
                if row["MACD"] > row["Signal"] and row["RSI"] < 70:
                    return "📈 BUY (LONG)"
                elif row["MACD"] < row["Signal"] and row["RSI"] > 30:
                    return "📉 SELL (SHORT)"
                else:
                    return "⏸️ HOLD"

            signal = generate_signal(latest)

            st.subheader(f"Signal for {symbol}")
            st.metric("Price", f"${latest['Close']:.2f}")
            st.metric("RSI", f"{latest['RSI']:.2f}")
            st.metric("MACD", f"{latest['MACD']:.2f}")
            st.metric("Signal Line", f"{latest['Signal']:.2f}")
            st.success(signal)

            st.line_chart(data[['Close', 'RSI']])
