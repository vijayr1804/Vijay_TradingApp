import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ultimate NSE Analyzer", layout="centered")

st.title("📈 Ultimate NSE Trading + Investor Analyzer")

symbol_input = st.text_input("Enter NSE Stock (example: reliance, tcs, itc)")

if st.button("Analyze"):

    if not symbol_input:
        st.warning("Please enter a stock name.")
        st.stop()

    symbol = symbol_input.strip().upper() + ".NS"

    df = yf.download(symbol, period="1y", auto_adjust=True)

    if df.empty:
        st.error("Invalid stock or no data available.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ================= INDICATORS =================
    df["20DMA"] = df["Close"].rolling(20).mean()
    df["50DMA"] = df["Close"].rolling(50).mean()
    df["200DMA"] = df["Close"].rolling(200).mean()
    df["AvgVol"] = df["Volume"].rolling(20).mean()
    df["20High"] = df["Close"].rolling(20).max()
    df["52High"] = df["Close"].rolling(252).max()
    df["52Low"] = df["Close"].rolling(252).min()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    df = df.dropna()

    # SAFETY CHECK (prevents IndexError)
    if len(df) < 2:
        st.error("Not enough historical data to calculate indicators.")
        st.stop()

    latest = df.iloc[-1].to_dict()
    previous = df.iloc[-2].to_dict()

    # ================= SHORT TERM STRENGTH =================
    cond1 = latest["Close"] > latest["20DMA"]
    cond2 = latest["Close"] > latest["50DMA"]
    cond3 = latest["Volume"] > latest["AvgVol"]
    cond4 = latest["RSI"] > 55

    strength_score = sum([cond1, cond2, cond3, cond4])

    if strength_score == 4:
        short_signal = "🟢 STRONG BUY"
    elif strength_score >= 2:
        short_signal = "🟡 WATCH"
    else:
        short_signal = "🔴 AVOID"

    breakout = latest["Close"] > previous["20High"]

    # ================= MARKET STAGE =================
    if latest["Close"] > latest["200DMA"] and latest["50DMA"] > latest["200DMA"]:
        stage = "Stage 2 (Uptrend)"
    elif latest["Close"] < latest["200DMA"] and latest["50DMA"] < latest["200DMA"]:
        stage = "Stage 4 (Downtrend)"
    elif latest["Close"] > latest["200DMA"] and latest["50DMA"] < latest["200DMA"]:
        stage = "Stage 1 (Accumulation)"
    else:
        stage = "Stage 3 (Distribution)"

    accumulation = (
        latest["Volume"] > latest["AvgVol"]
        and latest["Close"] > latest["50DMA"]
        and latest["RSI"] > 50
    )

    overheated = latest["RSI"] > 70

    # ================= OUTPUT =================

    st.subheader("🔥 Short-Term View")
    st.write(f"Strength Score: {strength_score} / 4")
    st.write(f"Signal: {short_signal}")

    if breakout:
        st.success("🚀 20-Day Breakout Detected")

    st.markdown("---")

    st.subheader("📊 Long-Term Investor View (1–2 Years)")
    st.write("Market Stage:", stage)

    if stage == "Stage 2 (Uptrend)":
        st.success("Strong long-term uptrend. Better to buy on dips near 50DMA.")
    elif stage == "Stage 1 (Accumulation)":
        st.info("Base formation. Institutions may be accumulating.")
    elif stage == "Stage 3 (Distribution)":
        st.warning("Possible topping phase. Avoid aggressive buying.")
    else:
        st.error("Long-term downtrend. Avoid long-term investing.")

    if accumulation:
        st.success("📦 Accumulation pattern detected")

    if overheated:
        st.warning("⚠ RSI above 70 → Short-term overheated")

    st.markdown("---")

    st.subheader("📈 Key Levels")
    st.write("Current Price:", round(latest["Close"], 2))
    st.write("20 DMA:", round(latest["20DMA"], 2))
    st.write("50 DMA:", round(latest["50DMA"], 2))
    st.write("200 DMA:", round(latest["200DMA"], 2))
    st.write("52 Week High:", round(latest["52High"], 2))
    st.write("52 Week Low:", round(latest["52Low"], 2))
    st.write("RSI:", round(latest["RSI"], 2))
    st.write("Volume Ratio:", round(latest["Volume"] / latest["AvgVol"], 2), "x")

    # ================= CHART =================
    fig, ax = plt.subplots()
    ax.plot(df["Close"], label="Close")
    ax.plot(df["50DMA"], label="50 DMA")
    ax.plot(df["200DMA"], label="200 DMA")
    ax.legend()
    st.pyplot(fig)
