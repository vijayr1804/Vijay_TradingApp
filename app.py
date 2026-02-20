import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ultimate NSE Stock Analyzer", layout="wide")

st.title("📊 Ultimate NSE Stock Analyzer")
st.markdown("Professional Trading + Investor Guidance System")

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

        # ===============================
        # Moving Averages
        # ===============================
        df["20DMA"] = df["Close"].rolling(20).mean()
        df["50DMA"] = df["Close"].rolling(50).mean()
        df["200DMA"] = df["Close"].rolling(200).mean()

        # ===============================
        # RSI Calculation
        # ===============================
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

        # ===============================
        # Strength Score
        # ===============================
        score = 0
        score += close > dma20
        score += close > dma50
        score += rsi > 50
        score += volume > avg_vol

        # ===============================
        # Signal Logic
        # ===============================
        if score >= 3 and close > dma50:
            signal = "BUY"
        elif score == 2:
            signal = "WATCH"
        else:
            signal = "AVOID"

        breakout = close > df["High"].rolling(20).max().iloc[-2]

        # Market Stage
        if close > dma200 and dma50 > dma200:
            stage = "Stage 2 - Strong Uptrend"
        elif close < dma200 and dma50 < dma200:
            stage = "Stage 4 - Downtrend"
        elif close > dma200:
            stage = "Stage 1 - Accumulation"
        else:
            stage = "Stage 3 - Distribution"

        accumulation = volume > avg_vol and close > dma50
        overheated = rsi > 75

        long_term = "Favorable for 1–2 Year Holding" if close > dma200 else "Wait for price above 200DMA for safer long-term entry"

        # ===============================
        # OUTPUT SECTION
        # ===============================

        st.subheader("📌 Core Technical Data")
        st.write(f"Current Price: ₹ {round(close,2)}")
        st.write(f"20DMA: ₹ {round(dma20,2)}")
        st.write(f"50DMA: ₹ {round(dma50,2)}")
        st.write(f"200DMA: ₹ {round(dma200,2)}")
        st.write(f"RSI: {round(rsi,2)}")
        st.write(f"52-Week High: ₹ {round(high_52,2)}")
        st.write(f"52-Week Low: ₹ {round(low_52,2)}")

        st.markdown("---")

        st.subheader("⚡ Trading Decision Summary")
        st.write(f"Strength Score: {score} / 4")
        st.write(f"Signal: {signal}")
        st.write(f"20-Day Breakout: {'Yes' if breakout else 'No'}")
        st.write(f"Market Stage: {stage}")
        st.write(f"Accumulation: {'Yes' if accumulation else 'No'}")
        st.write(f"Overheated: {'Yes' if overheated else 'No'}")
        st.write(f"Long-Term View: {long_term}")

        st.markdown("---")

        # ===============================
        # DETAILED EXPLANATION
        # ===============================

        st.subheader("📘 Detailed Explanation of Each Result")

        st.markdown(f"""
### 🔹 1. Strength Score ({score}/4)
This measures short-term momentum strength.
- 4/4 → Very strong momentum.
- 3/4 → Positive bullish setup.
- 2/4 → Mixed signals.
- 0–1 → Weak structure.

It combines price trend + RSI + volume confirmation.

---

### 🔹 2. Signal: {signal}
This gives a simplified action idea:
- BUY → Trend, momentum and volume aligned.
- WATCH → Some positive signals but not strong.
- AVOID → Weak technical structure.

---

### 🔹 3. 20-Day Breakout: {"Yes" if breakout else "No"}
If Yes, price is breaking recent 20-day high.
This often attracts traders and can trigger momentum moves.

---

### 🔹 4. Market Stage: {stage}
Based on 200DMA:
- Stage 1 → Base building phase.
- Stage 2 → Strong uptrend (best for trend traders).
- Stage 3 → Distribution phase.
- Stage 4 → Downtrend (avoid fresh long entries).

---

### 🔹 5. Accumulation: {"Yes" if accumulation else "No"}
High volume + rising price may indicate institutional buying.
This can be early sign of bigger moves.

---

### 🔹 6. Overheated: {"Yes" if overheated else "No"}
If RSI above 75, stock may be stretched.
Pullback risk increases.

---

### 🔹 7. Long-Term Guidance
{long_term}
200DMA acts as long-term trend filter.
Investors prefer price above 200DMA.
""")

        st.markdown("---")

        st.subheader("📉 Price Chart")
        st.line_chart(df[["Close", "20DMA", "50DMA", "200DMA"]])

    except Exception:
        st.error("Error occurred. Please check stock symbol.")
