import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional NSE Stock Analyzer", layout="wide")

st.title("📊 Professional NSE Stock Analyzer")
st.markdown("Advanced Technical + Investor Guidance Dashboard")

symbol_input = st.text_input("Enter NSE Stock (Example: RELIANCE, TCS, INFY)")

if symbol_input:

    symbol = symbol_input.upper().strip()
    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:
        df = yf.download(symbol, period="2y", auto_adjust=True)

        if df.empty or len(df) < 250:
            st.warning("⚠ Not enough historical data.")
            st.stop()

        df = df[["Close", "High", "Low", "Volume"]].copy()

        # =============================
        # Moving Averages
        # =============================
        df["20DMA"] = df["Close"].rolling(20).mean()
        df["50DMA"] = df["Close"].rolling(50).mean()
        df["200DMA"] = df["Close"].rolling(200).mean()

        # =============================
        # RSI
        # =============================
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df["AvgVolume20"] = df["Volume"].rolling(20).mean()

        df.dropna(inplace=True)

        latest = df.iloc[-1]

        close = float(latest["Close"])
        dma20 = float(latest["20DMA"])
        dma50 = float(latest["50DMA"])
        dma200 = float(latest["200DMA"])
        rsi = float(latest["RSI"])
        volume = float(latest["Volume"])
        avg_vol = float(latest["AvgVolume20"])

        high_52 = float(df["High"].rolling(252).max().iloc[-1])
        low_52 = float(df["Low"].rolling(252).min().iloc[-1])

        # =============================
        # Strength Score (Short Term)
        # =============================
        score = 0

        if close > dma20:
            score += 1
        if close > dma50:
            score += 1
        if rsi > 50:
            score += 1
        if volume > avg_vol:
            score += 1

        # =============================
        # Buy / Watch / Avoid
        # =============================
        if score >= 3 and close > dma50:
            signal = "✅ BUY"
        elif score == 2:
            signal = "👀 WATCH"
        else:
            signal = "❌ AVOID"

        # =============================
        # 20 Day Breakout
        # =============================
        breakout = close > df["High"].rolling(20).max().iloc[-2]

        # =============================
        # Market Stage (1–4)
        # =============================
        if close > dma200 and dma50 > dma200:
            stage = "Stage 2 (Uptrend)"
        elif close < dma200 and dma50 < dma200:
            stage = "Stage 4 (Downtrend)"
        elif close > dma200 and dma50 < dma200:
            stage = "Stage 1 (Accumulation)"
        else:
            stage = "Stage 3 (Distribution)"

        # =============================
        # Accumulation Detection
        # =============================
        accumulation = volume > avg_vol and close > dma50

        # =============================
        # Overheated Warning
        # =============================
        overheated = rsi > 75

        # =============================
        # Investor Guidance (1–2 Years)
        # =============================
        if close > dma200:
            long_term = "📈 Suitable for Long-Term Holding"
        else:
            long_term = "⚠ Wait for price above 200DMA for safer long-term entry"

        # =============================
        # OUTPUT SECTION
        # =============================

        st.subheader("📌 Key Metrics")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Close", round(close, 2))
        col2.metric("20 DMA", round(dma20, 2))
        col3.metric("50 DMA", round(dma50, 2))
        col4.metric("200 DMA", round(dma200, 2))

        col5, col6, col7 = st.columns(3)
        col5.metric("RSI", round(rsi, 2))
        col6.metric("52W High", round(high_52, 2))
        col7.metric("52W Low", round(low_52, 2))

        st.markdown("---")

        st.subheader("⚡ Trading Signals")
        st.write("Strength Score:", score, "/ 4")
        st.write("Signal:", signal)
        st.write("20-Day Breakout:", "🚀 YES" if breakout else "No breakout")
        st.write("Market Stage:", stage)
        st.write("Accumulation:", "📥 YES" if accumulation else "No")
        st.write("Overheated:", "🔥 RSI High" if overheated else "Healthy")

        st.markdown("---")

        st.subheader("🏦 Investor Guidance (1–2 Years)")
        st.write(long_term)

        st.markdown("---")

        st.subheader("📉 Price Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA", "200DMA"]])

        st.markdown("---")

        st.subheader("📘 Explanation Guide")

        st.markdown("""
- **Strength Score**: Short-term momentum strength (0–4).
- **BUY**: Strong trend + momentum confirmation.
- **20-Day Breakout**: Price breaking recent high.
- **Stage 2**: Strong uptrend phase.
- **Accumulation**: Institutions possibly buying.
- **Overheated**: RSI above 75 may cause pullback.
- **200DMA**: Long-term investor trend line.
- **52-Week Levels**: Important psychological zones.
""")

    except Exception:
        st.error("Error occurred. Check stock symbol.")
