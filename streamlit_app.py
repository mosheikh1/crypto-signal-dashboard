import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="centered")

st.title("📈 Crypto Futures Signal Dashboard")
st.markdown("Real-time BUY/SELL signals using RSI & MACD indicators.")

# Sidebar - user selects crypto pair and timeframe
symbol = st.sidebar.selectbox("Select Crypto Pair", ["BTC-USD", "ETH-USD", "SOL-USD"])
interval = st.sidebar.selectbox("Select Timeframe", ["1h", "4h", "1d"])
st.sidebar.markdown("⚠️ Data from Yahoo Finance")

@st.cache_data(ttl=300)
def get_data(symbol, interval):
    if interval == "1h":
        return yf.download(tickers=symbol, period="7d", interval="1h")
    elif interval == "4h":
        return yf.download(tickers=symbol, period="30d", interval="4h")
    else:  # daily
        return yf.download(tickers=symbol, period="90d", interval="1d")

data = get_data(symbol, interval)

if data.empty:
    st.error("❌ No data found for selected symbol/timeframe.")
else:
    if 'Close' not in data.columns:
        st.error("❌ 'Close' column not found in data.")
    else:
        # Check if we have enough data points
        if data['Close'].dropna().shape[0] < 50:
            st.error("❌ Not enough data to calculate indicators. Try another timeframe or symbol.")
        else:
            # Calculate indicators on full Close series
            rsi_indicator = ta.momentum.RSIIndicator(close=data['Close'])
            data['RSI'] = rsi_indicator.rsi()

            macd_indicator = ta.trend.MACD(close=data['Close'])
            data['MACD'] = macd_indicator.macd()
            data['Signal'] = macd_indicator.macd_signal()

            # Drop NaNs created by indicator calculation
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

                st.subheader(f"Signal for {symbol} ({interval})")
                st.metric("Price", f"${latest['Close']:.2f}")
                st.metric("RSI", f"{latest['RSI']:.2f}")
                st.metric("MACD", f"{latest['MACD']:.2f}")
                st.metric("Signal Line", f"{latest['Signal']:.2f}")
                st.success(signal)

                st.line_chart(data[['Close', 'RSI']])
