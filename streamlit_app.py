import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.set_page_config(page_title="Crypto Signal Dashboard", layout="centered")

st.title("📊 Crypto Futures Signal Dashboard")
st.markdown("Uses **RSI** and **MACD** to generate Long/Short signals for scalping & futures trading.")

# --- Sidebar for controls
symbol = st.sidebar.selectbox("Select Crypto Pair", ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"])
interval = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
st.sidebar.caption("⚠️ Source: Yahoo Finance")

# --- Function to load data
@st.cache_data(ttl=300)
def load_data(symbol, interval):
    if interval == "1h":
        data = yf.download(tickers=symbol, period="7d", interval="1h")
    elif interval == "4h":
        data = yf.download(tickers=symbol, period="30d", interval="4h")
    else:
        data = yf.download(tickers=symbol, period="90d", interval="1d")
    return data

data = load_data(symbol, interval)

# --- Check data
if data.empty or "Close" not in data.columns:
    st.error("❌ Failed to fetch valid data.")
else:
    try:
        close = data["Close"].dropna()

        # Ensure close is 1D Series
        close = pd.Series(close.values, index=close.index)

        # --- Compute RSI and MACD
        rsi = ta.momentum.RSIIndicator(close=close).rsi()
        macd_calc = ta.trend.MACD(close=close)
        macd_line = macd_calc.macd()
        signal_line = macd_calc.macd_signal()

        # Align lengths
        indicators = pd.DataFrame({
            "RSI": rsi,
            "MACD": macd_line,
            "Signal": signal_line
        }, index=close.index)

        data = data.join(indicators)

        # Drop missing
        data.dropna(inplace=True)

        # --- Get latest signal
        latest = data.iloc[-1]

        def get_signal(row):
            if row["MACD"] > row["Signal"] and row["RSI"] < 70:
                return "📈 BUY (LONG)"
            elif row["MACD"] < row["Signal"] and row["RSI"] > 30:
                return "📉 SELL (SHORT)"
            else:
                return "⏸️ HOLD"

        signal = get_signal(latest)

        # --- UI Display
        st.subheader(f"{symbol} - {interval} Signal")
        st.metric("Current Price", f"${latest['Close']:.2f}")
        st.metric("RSI", f"{latest['RSI']:.2f}")
        st.metric("MACD", f"{latest['MACD']:.4f}")
        st.metric("Signal Line", f"{latest['Signal']:.4f}")
        st.success(f"**{signal}**")

        # --- Charts
        st.line_chart(data[["Close"]], use_container_width=True)
        st.line_chart(data[["RSI"]], use_container_width=True)

    except Exception as e:
        st.error(f"Error calculating indicators: {e}")
