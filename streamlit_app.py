import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="centered")

# Title
st.title("📈 Crypto Futures Signal Dashboard")
st.markdown("Real-time BUY/SELL signals using RSI & MACD indicators.")

# Sidebar
symbol = st.sidebar.selectbox("Select Crypto Pair", ["BTC-USD", "ETH-USD", "SOL-USD"])
interval = st.sidebar.selectbox("Select Timeframe", ["1h", "4h", "1d"])
st.sidebar.markdown("Data from Yahoo Finance")

# Fetch data
@st.cache_data(ttl=300)
def get_data(symbol, interval):
    if interval == "1h":
        data = yf.download(tickers=symbol, period="7d", interval="1h")
    elif interval == "4h":
        data = yf.download(tickers=symbol, period="30d", interval="4h")
    else:
        data = yf.download(tickers=symbol, period="90d", interval="1d")
    return data

data = get_data(symbol, interval)

# Calculate indicators
if not data.empty and data['Close'].isnull().sum() == 0:
    data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['Signal'] = macd.macd_signal()
    latest = data.iloc[-1]

    def generate_signal(latest):
        if latest["MACD"] > latest["Signal"] and latest["RSI"] < 70:
            return "📈 BUY (LONG)"
        elif latest["MACD"] < latest["Signal"] and latest["RSI"] > 30:
            return "📉 SELL (SHORT)"
        else:
            return "⏸️ HOLD"

    signal = generate_signal(latest)

    st.subheader(f"Current Signal for {symbol}")
    st.metric("Price", f"${latest['Close']:.2f}")
    st.metric("RSI", f"{latest['RSI']:.2f}")
    st.metric("MACD", f"{latest['MACD']:.2f}")
    st.metric("Signal Line", f"{latest['Signal']:.2f}")
    st.success(signal)

    st.line_chart(data[['Close', 'RSI']].dropna())
else:
    st.error("Failed to load valid data. Try another pair or interval.")

macd = ta.trend.MACD(data['Close'])
data['MACD'] = macd.macd()
data['Signal'] = macd.macd_signal()

# Generate signal
def generate_signal(latest):
    if latest["MACD"] > latest["Signal"] and latest["RSI"] < 70:
        return "📈 BUY (LONG)"
    elif latest["MACD"] < latest["Signal"] and latest["RSI"] > 30:
        return "📉 SELL (SHORT)"
    else:
        return "⏸️ HOLD"

latest = data.iloc[-1]
signal = generate_signal(latest)

# Display
st.subheader(f"Current Signal for {symbol}")
st.metric("Price", f"${latest['Close']:.2f}")
st.metric("RSI", f"{latest['RSI']:.2f}")
st.metric("MACD", f"{latest['MACD']:.2f}")
st.metric("Signal Line", f"{latest['Signal']:.2f}")
st.success(signal)

# Chart
st.line_chart(data[['Close', 'RSI']].dropna())
