import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional NSE Analyzer", layout="wide")

st.title("📊 Professional NSE Stock Analysis System")

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

        # Signal
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
            stage = "Stage 2 – Strong Uptrend"
        elif close < dma200 and dma50 < dma200:
            stage = "Stage 4 – Downtrend"
        elif close > dma200:
            stage = "Stage 1 – Accumulation Phase"
        else:
            stage = "Stage 3 – Distribution Phase"

        accumulation = volume > avg_vol and close > dma50
        overheated = rsi > 75

        long_term = (
            "Suitable for long-term holding (price above 200DMA)."
            if close > dma200
            else "Wait for sustained move above 200DMA before long-term entry."
        )

        # ================= OUTPUT =================

        st.subheader("📌 Core Technical Levels")
        st.write(f"Current Price: ₹ {round(close,2)}")
        st.write(f"20DMA: ₹ {round(dma20,2)}")
        st.write(f"50DMA: ₹ {round(dma50,2)}")
        st.write(f"200DMA: ₹ {round(dma200,2)}")
        st.write(f"RSI: {round(rsi,2)}")
        st.write(f"52-Week High: ₹ {round(high_52,2)}")
        st.write(f"52-Week Low: ₹ {round(low_52,2)}")

        st.markdown("---")

        st.subheader("⚡ Trading Signals")
        st.write(f"Strength Score (Short Term): {score}/4")
        st.write(f"Buy / Watch / Avoid Signal: {signal}")
        st.write(f"20-Day Breakout Detection: {'YES' if breakout else 'NO'}")
        st.write(f"Market Stage (1–4): {stage}")
        st.write(f"Accumulation Detection: {'YES' if accumulation else 'NO'}")
        st.write(f"Overheated Warning: {'YES – RSI High' if overheated else 'NO'}")
        st.write(f"1–2 Year Investor Guidance: {long_term}")

        st.markdown("---")

        st.subheader("📘 Detailed Professional Explanation")

        st.markdown(f"""
### 🔹 Strength Score ({score}/4)
Measures short-term technical strength.
- 4/4 = Strong bullish momentum.
- 3/4 = Positive setup.
- 2/4 = Mixed signals.
- 0–1 = Weak structure.

### 🔹 Signal: {signal}
BUY = Trend + momentum aligned.
WATCH = Wait for confirmation.
AVOID = Weak technical structure.

### 🔹 20-Day Breakout
If YES, stock is breaking recent highs.
Breakouts attract momentum traders.

### 🔹 Market Stage: {stage}
Stage 2 = Strong trending phase.
Stage 4 = Downtrend (avoid fresh buying).

### 🔹 Accumulation
High volume + rising price suggests institutional interest.

### 🔹 Overheated Warning
If RSI above 75, pullback risk increases.

### 🔹 Long-Term View
200DMA acts as long-term trend filter.
Investors prefer price above 200DMA.
""")

        st.markdown("---")

        st.subheader("📉 Price Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA", "200DMA"]])

    except Exception:
        st.error("Error occurred. Please check stock symbol.")
