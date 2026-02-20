import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("📈 Trading Strength Web App")

symbol_input = st.text_input("Enter NSE Stock (example: reliance, tcs, itc)")

if st.button("Analyze"):

    symbol = symbol_input.strip().upper() + ".NS"
    df = yf.download(symbol, period="6mo", auto_adjust=True)

    if df.empty:
        st.error("Invalid stock name")
    else:
        df["20DMA"] = df["Close"].rolling(20).mean()
        df["50DMA"] = df["Close"].rolling(50).mean()
        df["AvgVol"] = df["Volume"].rolling(20).mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100/(1+rs))

        latest = df.tail(1).iloc[0]

        score = 0
        if latest["Close"] > latest["20DMA"]:
            score += 1
        if latest["Close"] > latest["50DMA"]:
            score += 1
        if latest["Volume"] > latest["AvgVol"]:
            score += 1
        if latest["RSI"] > 55:
            score += 1

        st.subheader(f"Strength Score: {score} / 4")
        st.write("Latest Close:", round(latest["Close"],2))
        st.write("RSI:", round(latest["RSI"],2))

        fig, ax = plt.subplots()
        ax.plot(df["Close"], label="Close")
        ax.plot(df["20DMA"], label="20DMA")
        ax.plot(df["50DMA"], label="50DMA")
        ax.legend()
        st.pyplot(fig)
