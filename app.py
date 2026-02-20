import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smart NSE Stock Analyzer", layout="wide")

st.title("📈 Smart NSE Stock Analyzer (Professional Version)")
st.markdown("Analyze NSE stocks using Moving Averages & RSI Strategy")

symbol = st.text_input("Enter NSE Stock Name (Example: RELIANCE, TCS, INFY)")

if symbol:

    # Automatically add .NS if not provided
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol = symbol + ".NS"

    # Download data
    df = yf.download(symbol, period="6mo")

    if df.empty:
        st.error("❌ Invalid stock name or no data available on Yahoo Finance.")
    else:
        if len(df) < 60:
            st.warning("⚠ Not enough historical data to calculate full indicators (need 60+ days).")
        else:
            # Moving averages
            df["20DMA"] = df["Close"].rolling(20).mean()
            df["50DMA"] = df["Close"].rolling(50).mean()

            # RSI Calculation
            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            df.dropna(inplace=True)

            if df.empty:
                st.warning("⚠ Not enough clean data after indicator calculation.")
            else:
                latest = df.iloc[-1]

                # Strength Score Calculation
                score = 0

                if latest["Close"] > latest["20DMA"]:
                    score += 1

                if latest["Close"] > latest["50DMA"]:
                    score += 1

                if latest["RSI"] > 50:
                    score += 1

                if latest["RSI"] < 70:
                    score += 1

                # -----------------------------
                # OUTPUT SECTION
                # -----------------------------

                st.subheader("📊 Latest Stock Analysis")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("Latest Close", round(latest["Close"], 2))
                col2.metric("20 DMA", round(latest["20DMA"], 2))
                col3.metric("50 DMA", round(latest["50DMA"], 2))
                col4.metric("RSI", round(latest["RSI"], 2))

                st.markdown("---")

                st.subheader("📈 Strength Score")
                st.write(f"Score: {score} / 4")

                if score == 4:
                    st.success("🔥 Very Strong Bullish Trend")
                elif score == 3:
                    st.info("👍 Positive Trend")
                elif score == 2:
                    st.warning("⚖ Neutral / Sideways")
                else:
                    st.error("🔻 Weak / Bearish Trend")

                st.markdown("---")

                # -----------------------------
                # EDUCATIONAL EXPLANATION
                # -----------------------------

                st.subheader("📘 What These Indicators Mean")

                st.markdown("""
### 1️⃣ 20 Day Moving Average (Short Term Trend)
- Shows short-term price direction.
- If price is above 20DMA → short-term bullish.
- If below → short-term weakness.

### 2️⃣ 50 Day Moving Average (Medium Term Trend)
- Shows medium-term trend.
- Price above 50DMA → strong structure.
- Price below → weakness in structure.

### 3️⃣ RSI (Relative Strength Index)
- Measures momentum (0 to 100 scale).
- Above 70 → Overbought (possible pullback).
- Below 30 → Oversold (possible bounce).
- Between 50–70 → Healthy bullish momentum.

### 4️⃣ Strength Score Logic
We combine all signals:
- Price > 20DMA ✔
- Price > 50DMA ✔
- RSI > 50 ✔
- RSI < 70 ✔

More ✔ = stronger stock.
""")

                st.markdown("---")

                # Chart
                st.subheader("📉 Price Chart with Moving Averages")
                st.line_chart(df[["Close", "20DMA", "50DMA"]])
