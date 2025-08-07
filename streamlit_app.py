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
elif 'Close' not in data.columns:
    st.error("❌ 'Close' column not found in data.")
else:
    try:
        # Convert to 1D Series properly
        close_series = data['Close'].dropna()
        close_series = pd.Series(close_series.values.flatten(), index=close_series.index)

        if len(close_series) < 50:
            st.error("❌ Not enough data points to calculate indicators.")
        else:
            # Calculate RSI and MACD
            rsi = ta.momentum.RSIIndicator(close=close_series).rsi()
            macd = ta.trend.MACD(close=close_series)
            macd_line = macd.macd()
            signal_line = macd.macd_signal()

            # Merge into the original dataframe
            data['RSI'] = rsi
            data['MACD'] = macd_line
            data['Signal'] = signal_line
            data.dropna(subset=['RSI', 'MACD', 'Signal'], inplace=True)

            if data.empty:
                st.error("❌ No data left after calculating indicators.")
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

    except Exception as e:
        st.error(f"Error calculating indicators: {e}")
        st.write("Make sure your data contains a valid 'Close' column with numeric values.")
