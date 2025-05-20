# 📈 Algo Trading Bot with Upstox API

## 🧠 Overview
A fully automated stock trading bot built using the Upstox API. It implements technical trading strategies like moving average crossovers and supports live paper trading, backtesting, and future AI integrations.

## ⚙️ Tech Stack
- Python
- Upstox API (v2/v3)
- Backtrader / bt
- Pandas, NumPy,Pandas ta
- SQLite (for trade logs)
- Streamlit (for dashboard - optional)
- SpeechRecognition + OpenAI (future enhancement)

## 🔑 Features
- ✔️ Login & session management with Upstox API
- 📊 Fetches historical & live OHLCV data
- 📉 Implements Moving Average Crossover strategy
- 🔁 Backtesting with performance metrics
- 🟢 Live paper trading (non-real money mode)
- 🗣️ Future: Voice-based or GPT-driven command system
- 📈 Logs trades, returns, win/loss rates

## 🖥️ Strategy Example: Moving Average Crossover

> Entry: When 20-day MA crosses above 50-day MA  
> Exit: When 20-day MA crosses below 50-day MA  
> Risk: ₹X per trade or 1% of capital  
> Timeframe: Daily or 15-minute data

## 📦 Installation & Setup
```bash
git clone https://github.com/yourusername/algo-trader-upstox
cd algo-trader-upstox
pip install -r requirements.txt
python scripts/login_upstox.py  # setup token
python live_trading/trader.py
