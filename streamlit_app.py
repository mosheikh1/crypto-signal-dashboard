import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="wide")
st.title("🚀 Crypto Signal Dashboard (RSI + MACD)")

symbol = st.text_input("Enter a crypto symbol (e.g., BTC-USD, ETH-USD):", "BTC-USD")
interval = st.selectbox("Select interval:", ["1m", "5m", "15m", "1h", "1d"], index=2)
period = st.selectbox("Select historical period:", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=1)

# Download data from yfinance
try:
    data = yf.download(tickers=symbol, period=period, interval=interval)
    if data.empty or "Close" not in data.columns:
        st.error("No data found. Please check the symbol or try again later.")
        st.stop()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

try:
    # Ensure 'Close' is a 1D Series
    close = data["Close"].dropna()
    if len(close.shape) > 1:
        close = close.squeeze()

    # Calculate indicators
    rsi = ta.momentum.RSIIndicator(close=close).rsi()
    macd_calc = ta.trend.MACD(close=close)
    macd_line = macd_calc.macd()
    signal_line = macd_calc.macd_signal()

    # Merge indicators into original dataframe
    data = data.loc[close.index]  # Align with cleaned close
    data["RSI"] = rsi
    data["MACD"] = macd_line
    data["Signal"] = signal_line
    data.dropna(inplace=True)

    if data.empty:
        st.error("Indicators could not be calculated (no data after cleanup).")
        st.stop()

    # Get latest signal
    latest = data.iloc[-1]
    def generate_signal(row):
        if row["MACD"] > row["Signal"] and row["RSI"] < 70:
            return "📈 BUY (LONG)"
        elif row["MACD"] < row["Signal"] and row["RSI"] > 30:
            return "📉 SELL (SHORT)"
        else:
            return "⏸️ HOLD"

    signal = generate_signal(latest)

    # Display metrics
    st.subheader(f"Signal for {symbol}")
    st.metric("Price", f"${latest['Close']:.2f}")
    st.metric("RSI", f"{latest['RSI']:.2f}")
    st.metric("MACD", f"{latest['MACD']:.4f}")
    st.metric("Signal Line", f"{latest['Signal']:.4f}")
    st.success(signal)

    # Chart
    st.line_chart(data[["Close", "RSI"]])

except Exception as e:
    st.error(f"Error calculating indicators: {e}")
    st.stop()
