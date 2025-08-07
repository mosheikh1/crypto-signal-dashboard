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
if 'Close' in data.columns:
    close_prices = data['Close'].dropna()

    if not close_prices.empty:
        # Calculate indicators
        rsi_indicator = ta.momentum.RSIIndicator(close=close_prices)
        data['RSI'] = rsi_indicator.rsi()

        macd_indicator = ta.trend.MACD(close=close_prices)
        data['MACD'] = macd_indicator.macd()
        data['Signal'] = macd_indicator.macd_signal()

        data.dropna(inplace=True)

        if not data.empty:
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

            st.line_chart(data[['Close', 'RSI']])
        else:
            st.error("📉 Not enough data after indicator calculation.")
    else:
        st.error("⚠️ 'Close' prices are missing or all NaN.")
else:
    st.error("⚠️ No 'Close' column found in data.")


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
