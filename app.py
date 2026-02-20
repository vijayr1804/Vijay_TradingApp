import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trading Strength App", layout="centered")

st.title("📈 NSE Stock Strength Analyzer")

st.write("Enter NSE stock name (Example: reliance, tcs, itc, hdfcbank)")

symbol_input = st.text_input("Stock Name")

if st.button("Analyze"):

    if symbol_input.strip() == "":
        st.warning("Please enter a stock name.")
    else:
        symbol = symbol_input.strip().upper() + ".NS"

        df = yf.download(symbol, period="6mo", auto_adjust=True)

        if df.empty:
            st.error("Invalid stock name or data not available.")
        else:
            # Moving averages
            df["20DMA"] = df["Close"].rolling(20).mean()
            df["50DMA"] = df["Close"].rolling(50).mean()
            df["AvgVol"] = df["Volume"].rolling(20).mean()

            # RSI Calculation
            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            df["RSI"] = 100 - (100 / (1 + rs))

            df = df.dropna()

            if df.empty:
                st.error("Not enough data to calculate indicators.")
            else:
                latest = df.iloc[-1]

                score = 0

                if latest["Close"] > latest["20DMA"]:
                    score += 1
                if latest["Close"] > latest["50DMA"]:
                    score += 1
                if latest["Volume"] > latest["AvgVol"]:
                    score += 1
                if latest["RSI"] > 55:
                    score += 1

                st.subheader(f"🔥 Strength Score: {score} / 4")

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
