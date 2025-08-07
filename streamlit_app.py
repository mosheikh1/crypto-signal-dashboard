import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="centered")

st.title("📊 Crypto Futures Signal Dashboard")
st.markdown("Get technical analysis signals for **Long/Short** scalping strategies using RSI & MACD.")

# --- Sidebar
symbol = st.sidebar.selectbox("Select Crypto Pair", ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"])
interval = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
st.sidebar.caption("Data source: Yahoo Finance")

# --- Load Data Function
@st.cache_data(ttl=300)
def load_data(symbol, interval):
    period_map = {"1h": "7d", "4h": "30d", "1d": "90d"}
    data = yf.download(tickers=symbol, period=period_map[interval], interval=interval)
    return data

data = load_data(symbol, interval)

if data.empty or "Close" not in data.columns:
    st.error("❌ Failed to load valid data.")
else:
    try:
        # --- Clean and flatten Close column
        close = pd.Series(data["Close"].dropna().values, index=data["Close"].dropna().index)

        # --- Calculate Indicators
        rsi = ta.momentum.RSIIndicator(close=close).rsi()
        macd_calc = ta.trend.MACD(close=close)
        macd_line = macd_calc.macd()
        signal_line = macd_calc.macd_signal()

        # --- Join into main DataFrame
        indicators = pd.DataFrame({
            "RSI": rsi,
            "MACD": macd_line,
            "Signal": signal_line
        }, index=close.index)

        data = data.join(indicators)
        data.dropna(inplace=True)

        latest = data.iloc[-1]

        # --- Signal Logic
        def get_signal(row):
            if row["MACD"] > row["Signal"] and row["RSI"] < 70:
                return "📈 BUY (LONG)"
            elif row["MACD"] < row["Signal"] and row["RSI"] > 30:
                return "📉 SELL (SHORT)"
            else:
                return "⏸️ HOLD"

        signal = get_signal(latest)

        # --- Display
        st.subheader(f"{symbol} - {interval} Signal")
        st.metric("Current Price", f"${latest['Close']:.2f}")
        st.metric("RSI", f"{latest['RSI']:.2f}")
        st.metric("MACD", f"{latest['MACD']:.4f}")
        st.metric("Signal Line", f"{latest['Signal']:.4f}")
        st.success(f"**{signal}**")

        st.line_chart(data["Close"], use_container_width=True)
        st.line_chart(data["RSI"], use_container_width=True)

    except Exception as e:
        st.error(f"Error calculating indicators: {e}")
