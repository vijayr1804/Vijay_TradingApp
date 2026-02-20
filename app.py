import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional NSE Stock Analyzer", layout="wide")

st.title("📊 Professional NSE Stock Analyzer")
st.markdown("Advanced Trading + Investor Decision Dashboard")

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

        # Moving Averages
        df["20DMA"] = df["Close"].rolling(20).mean()
        df["50DMA"] = df["Close"].rolling(50).mean()
        df["200DMA"] = df["Close"].rolling(200).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df["AvgVol20"] = df["Volume"].rolling(20).mean()

        df.dropna(inplace=True)

        latest = df.iloc[-1]

        close = float(latest["Close"])
        dma20 = float(latest["20DMA"])
        dma50 = float(latest["50DMA"])
        dma200 = float(latest["200DMA"])
        rsi = float(latest["RSI"])
        volume = float(latest["Volume"])
        avg_vol = float(latest["AvgVol20"])

        high_52 = float(df["High"].rolling(252).max().iloc[-1])
        low_52 = float(df["Low"].rolling(252).min().iloc[-1])

        # Strength Score
        score = 0
        score += close > dma20
        score += close > dma50
        score += rsi > 50
        score += volume > avg_vol

        # Trading Signal
        if score >= 3 and close > dma50:
            signal = "BUY"
        elif score == 2:
            signal = "WATCH"
        else:
            signal = "AVOID"

        # Breakout
        breakout = close > df["High"].rolling(20).max().iloc[-2]

        # Market Stage
        if close > dma200 and dma50 > dma200:
            stage = "Stage 2 (Strong Uptrend)"
        elif close < dma200 and dma50 < dma200:
            stage = "Stage 4 (Downtrend)"
        elif close > dma200:
            stage = "Stage 1 (Accumulation Phase)"
        else:
            stage = "Stage 3 (Distribution Phase)"

        accumulation = volume > avg_vol and close > dma50
        overheated = rsi > 75

        long_term = "Good for Long-Term Holding" if close > dma200 else "Wait for 200DMA breakout"

        # ================= OUTPUT =================

        st.subheader("📌 Key Metrics")
        st.write(f"**Current Price:** {round(close,2)}")
        st.write(f"**20 DMA:** {round(dma20,2)}")
        st.write(f"**50 DMA:** {round(dma50,2)}")
        st.write(f"**200 DMA:** {round(dma200,2)}")
        st.write(f"**RSI:** {round(rsi,2)}")
        st.write(f"**52-Week High:** {round(high_52,2)}")
        st.write(f"**52-Week Low:** {round(low_52,2)}")

        st.markdown("---")

        st.subheader("⚡ Trading Summary")
        st.write("Strength Score:", score, "/ 4")
        st.write("Signal:", signal)
        st.write("20-Day Breakout:", "YES" if breakout else "No")
        st.write("Market Stage:", stage)
        st.write("Accumulation:", "YES" if accumulation else "No")
        st.write("Overheated:", "YES (RSI High)" if overheated else "No")

        st.markdown("---")

        st.subheader("📘 Detailed Explanation")

        st.markdown(f"""
### 🔹 Strength Score ({score}/4)
Measures short-term strength.
- Above 3 → Strong momentum.
- Below 2 → Weak momentum.

### 🔹 Signal: {signal}
- BUY → Trend + momentum aligned.
- WATCH → Mixed signals.
- AVOID → Weak structure.

### 🔹 20-Day Breakout: {"Yes" if breakout else "No"}
If YES → Stock breaking recent high → Possible momentum move.

### 🔹 Market Stage: {stage}
- Stage 2 = Best phase for trending stocks.
- Stage 4 = Downtrend, avoid fresh entries.

### 🔹 Accumulation: {"Yes" if accumulation else "No"}
High volume + rising price may indicate institutional buying.

### 🔹 Overheated: {"Yes" if overheated else "No"}
If RSI > 75 → Pullback risk.

### 🔹 Long-Term View
{long_term}
200DMA acts as long-term trend filter.
""")

        st.markdown("---")
        st.subheader("📉 Price Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA", "200DMA"]])

    except Exception:
        st.error("Error occurred. Please check stock symbol.")
