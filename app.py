import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Investor Strength App", layout="centered")

st.title("📈 NSE Investor Strength Analyzer (1–2 Year Mode)")

symbol_input = st.text_input("Enter NSE Stock (example: reliance, tcs, itc)")

if st.button("Analyze"):

    if not symbol_input:
        st.warning("Please enter a stock name.")
        st.stop()

    symbol = symbol_input.strip().upper() + ".NS"

    df = yf.download(symbol, period="1y", auto_adjust=True)

    if df.empty:
        st.error("Invalid stock or no data.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Indicators
    df["20DMA"] = df["Close"].rolling(20).mean()
    df["50DMA"] = df["Close"].rolling(50).mean()
    df["200DMA"] = df["Close"].rolling(200).mean()
    df["AvgVol"] = df["Volume"].rolling(20).mean()
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

    latest = df.iloc[-1].to_dict()

    # ===== Stage Detection =====
    stage = ""

    if latest["Close"] > latest["200DMA"] and latest["50DMA"] > latest["200DMA"]:
        stage = "Stage 2 (Uptrend)"
    elif latest["Close"] < latest["200DMA"] and latest["50DMA"] < latest["200DMA"]:
        stage = "Stage 4 (Downtrend)"
    elif latest["Close"] > latest["200DMA"] and latest["50DMA"] < latest["200DMA"]:
        stage = "Stage 1 (Accumulation)"
    else:
        stage = "Stage 3 (Distribution)"

    # ===== Accumulation Logic =====
    accumulation = (
        latest["Volume"] > latest["AvgVol"]
        and latest["Close"] > latest["50DMA"]
        and latest["RSI"] > 50
    )

    # ===== Overheated Warning =====
    overheated = latest["RSI"] > 70

    # ===== Long Term Investor Suggestion =====
    st.subheader("📊 Market Stage")
    st.write(stage)

    st.markdown("## 🧠 What This Means")

    if stage == "Stage 2 (Uptrend)":
        st.success("Strong long-term uptrend. Suitable for holding on dips.")
    elif stage == "Stage 1 (Accumulation)":
        st.info("Early stage base formation. Institutions may be accumulating.")
    elif stage == "Stage 3 (Distribution)":
        st.warning("Stock may be topping out. Caution required.")
    else:
        st.error("Long-term downtrend. Avoid long-term buying.")

    if accumulation:
        st.success("📦 Accumulation Signs: Volume + Trend alignment detected.")
    else:
        st.write("No strong accumulation pattern currently.")

    if overheated:
        st.warning("⚠ RSI above 70 → Stock may be short-term overheated.")

    st.markdown("## 📈 Key Levels")

    st.write("Latest Price:", round(latest["Close"], 2))
    st.write("200 DMA (Long-term trend):", round(latest["200DMA"], 2))
    st.write("52 Week High:", round(latest["52High"], 2))
    st.write("52 Week Low:", round(latest["52Low"], 2))
    st.write("RSI:", round(latest["RSI"], 2))

    # Chart
    fig, ax = plt.subplots()
    ax.plot(df["Close"], label="Close Price")
    ax.plot(df["50DMA"], label="50 DMA")
    ax.plot(df["200DMA"], label="200 DMA")
    ax.legend()
    st.pyplot(fig)
