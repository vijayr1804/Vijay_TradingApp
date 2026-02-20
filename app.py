import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart NSE Analyzer", layout="wide")

st.title("📈 Smart NSE Stock Analyzer")

# Input always visible
symbol_input = st.text_input("Enter NSE Stock Name (Example: RELIANCE, TCS, INFY)")

if symbol_input:

    symbol = symbol_input.upper().strip()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    try:
        df = yf.download(symbol, period="6mo", auto_adjust=True)

        if df.empty or len(df) < 60:
            st.warning("⚠ Not enough historical data available.")
            st.stop()

        # Keep only required columns
        df = df[["Close"]]

        # Indicators
        df["20DMA"] = df["Close"].rolling(20).mean()
        df["50DMA"] = df["Close"].rolling(50).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df.dropna(inplace=True)

        if df.empty:
            st.warning("⚠ Not enough clean data after calculations.")
            st.stop()

        # SAFELY extract single values
        latest_close = float(df["Close"].iloc[-1])
        latest_20dma = float(df["20DMA"].iloc[-1])
        latest_50dma = float(df["50DMA"].iloc[-1])
        latest_rsi = float(df["RSI"].iloc[-1])

        # Score calculation (now no error possible)
        score = 0
        if latest_close > latest_20dma:
            score += 1
        if latest_close > latest_50dma:
            score += 1
        if latest_rsi > 50:
            score += 1
        if latest_rsi < 70:
            score += 1

        # ---------------- OUTPUT ----------------

        st.subheader("📊 Latest Analysis")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Close", round(latest_close, 2))
        col2.metric("20 DMA", round(latest_20dma, 2))
        col3.metric("50 DMA", round(latest_50dma, 2))
        col4.metric("RSI", round(latest_rsi, 2))

        st.markdown("---")

        st.subheader("📈 Strength Score")
        st.write(f"Score: {score} / 4")

        if score == 4:
            st.success("🔥 Very Strong Bullish Trend")
        elif score == 3:
            st.info("👍 Positive Trend")
        elif score == 2:
            st.warning("⚖ Neutral")
        else:
            st.error("🔻 Weak Trend")

        st.markdown("---")

        st.subheader("📉 Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA"]])

    except Exception as e:
        st.error("Something went wrong. Please check stock symbol.")
