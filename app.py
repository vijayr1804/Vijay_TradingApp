import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Professional NSE Trading System", layout="wide")
st.title("📊 Professional NSE Trading & Investment System")

symbol_input = st.text_input("Enter NSE Stock (Example: RELIANCE, TCS, INFY)")

if symbol_input:

    symbol = symbol_input.upper().strip()
    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:
        df = yf.download(symbol, period="2y", auto_adjust=True)

        if df.empty or len(df) < 250:
            st.warning("Not enough historical data.")
            st.stop()

        df = df[["Close", "High", "Low", "Volume"]].copy()

        # Moving averages
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
        df["20DayHigh"] = df["High"].rolling(20).max()
        df["20DayLow"] = df["Low"].rolling(20).min()

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
        breakout_20 = close > float(latest["20DayHigh"])

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

        # Market Stage Detection
        if close > dma200 and dma50 > dma200:
            stage = "Stage 2 (Uptrend)"
        elif close > dma200 and dma50 < dma200:
            stage = "Stage 1 (Base Formation)"
        elif close < dma200 and dma50 < dma200:
            stage = "Stage 4 (Downtrend)"
        else:
            stage = "Stage 3 (Distribution)"

        # Accumulation Detection
        accumulation = (
            abs(close - dma200) / dma200 < 0.03 and
            volume > avg_vol and
            rsi > 45 and rsi < 60
        )

        # Overheated Detection
        overheated = rsi > 70 and close > dma20 * 1.08

        # ================= OUTPUT =================

        st.header("📊 PROFESSIONAL ANALYSIS REPORT")

        st.subheader("🔹 Core Price Data")
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
        st.write(f"20-Day Breakout Detection: {'YES' if breakout_20 else 'NO'}")
        st.write(f"Market Stage (1–4): {stage}")
        st.write(f"Accumulation Detection: {'YES' if accumulation else 'NO'}")
        st.write(f"Overheated Warning: {'YES ⚠' if overheated else 'NO'}")

        st.markdown("---")

        st.subheader("📘 Detailed Professional Explanation")

        explanation = f"""
### Trend Structure
- Price vs 20DMA → {'Bullish short-term momentum' if close > dma20 else 'Short-term weakness'}
- Price vs 50DMA → {'Healthy medium-term structure' if close > dma50 else 'Medium-term bearish pressure'}
- Price vs 200DMA → {'Long-term uptrend intact' if close > dma200 else 'Long-term structure weak'}

### Strength Score ({score}/4)
Score is based on trend alignment, RSI strength, and volume participation.
Higher score indicates stronger probability setup.

### Breakout Analysis
{'Stock is breaking above 20-day high indicating fresh buying momentum.' if breakout_20 else 'No breakout above 20-day high. Momentum confirmation missing.'}

### Market Stage
Current structure classified as: {stage}.
Stage 2 is strongest for positional trades.
Stage 4 is weakest and high-risk.

### Accumulation Check
{'Possible institutional accumulation detected near 200DMA.' if accumulation else 'No strong accumulation pattern detected.'}

### Overheated Risk
{'Stock appears overheated. Risk of pullback high.' if overheated else 'No overheating signs currently.'}

### 1–2 Year Investor Guidance
{'Structure supports long-term holding with dips accumulation strategy.' if close > dma200 else 'Wait for price to reclaim 200DMA before long-term aggressive buying.'}
"""

        st.markdown(explanation)

        st.markdown("---")
        st.subheader("📉 Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA", "200DMA"]])

    except Exception as e:
        st.error("Error fetching stock data. Check symbol.")
