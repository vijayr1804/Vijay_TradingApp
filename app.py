import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trading Strength App", layout="centered")

st.title("📈 NSE Stock Strength Analyzer (Learning Edition)")

st.write("Enter NSE stock symbol (example: reliance, tcs, itc, hdfcbank)")

symbol_input = st.text_input("Stock Name")

if st.button("Analyze"):

    if symbol_input.strip() == "":
        st.warning("Please enter a stock name.")
        st.stop()

    symbol = symbol_input.strip().upper() + ".NS"

    df = yf.download(symbol, period="6mo", auto_adjust=True)

    if df.empty:
        st.error("Invalid stock name or data not available.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicators
    df["20DMA"] = df["Close"].rolling(20).mean()
    df["50DMA"] = df["Close"].rolling(50).mean()
    df["AvgVol"] = df["Volume"].rolling(20).mean()
    df["20High"] = df["Close"].rolling(20).max()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df = df.dropna()

    latest = df.iloc[-1].to_dict()
    previous = df.iloc[-2].to_dict()

    # Strength Score
    score = 0

    cond1 = latest["Close"] > latest["20DMA"]
    cond2 = latest["Close"] > latest["50DMA"]
    cond3 = latest["Volume"] > latest["AvgVol"]
    cond4 = latest["RSI"] > 55

    score = sum([cond1, cond2, cond3, cond4])

    # Signal
    if score == 4:
        signal = "🟢 STRONG BUY"
    elif score >= 2:
        signal = "🟡 WATCH"
    else:
        signal = "🔴 AVOID"

    breakout = latest["Close"] > previous["20High"]

    st.subheader(f"🔥 Strength Score: {score} / 4")
    st.subheader(f"📊 Signal: {signal}")

    # Detailed Explanation Section
    st.markdown("## 📖 What This Means")

    if cond1:
        st.write("✅ Price is above 20DMA → Short-term trend is positive.")
    else:
        st.write("❌ Price is below 20DMA → Short-term weakness.")

    if cond2:
        st.write("✅ Price is above 50DMA → Medium-term trend is strong.")
    else:
        st.write("❌ Price is below 50DMA → Medium-term trend weak.")

    if cond3:
        st.write("✅ Volume is above average → Buyers are active (possible accumulation).")
    else:
        st.write("❌ Volume is below average → No strong buying interest.")

    if cond4:
        st.write("✅ RSI above 55 → Momentum is positive.")
    else:
        st.write("❌ RSI below 55 → Momentum is weak.")

    if breakout:
        st.success("🚀 20-Day Breakout → Price making new short-term high. Institutions may be entering.")

    st.markdown("## 📊 Indicator Values")

    st.write("Latest Close:", round(latest["Close"], 2))
    st.write("20 DMA:", round(latest["20DMA"], 2))
    st.write("50 DMA:", round(latest["50DMA"], 2))
    st.write("RSI:", round(latest["RSI"], 2))
    st.write("Volume vs Avg Volume:",
             round(latest["Volume"] / latest["AvgVol"], 2), "x")

    # Chart
    fig, ax = plt.subplots()
    ax.plot(df["Close"], label="Close Price")
    ax.plot(df["20DMA"], label="20 DMA")
    ax.plot(df["50DMA"], label="50 DMA")
    ax.legend()
    st.pyplot(fig)
