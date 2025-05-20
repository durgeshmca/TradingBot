import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# ------------------ Load Your Data ------------------
def load_data(symbol):
    # symbol = 'RELIANCE.NS'
    df = yf.download(symbol, start="2025-05-15", end="2025-05-16",interval='1m')
    print(df)
    df = df.reset_index()
    print(df.columns)
    # df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    df['timestamp']= df['Datetime']
    df = df.sort_values('timestamp')
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df.to_csv(f'{symbol}.csv')
    return df

# ------------------ Add Indicators ------------------
def add_indicators(df):
    df['RSI'] = ta.rsi(df['Close'], length=14)

    macd = ta.macd(df['Close'], fast=12, sLow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']

    supertrend = ta.supertrend(df['High'], df['Low'], df['Close'], length=20, multiplier=2.0)
    df['SUPERTREND'] = supertrend['SUPERT_20_2.0']
    df = df.set_index('timestamp')
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])

    return df.dropna()

# ------------------ Performance Metrics ------------------
def calculate_performance_metrics(returns, equity_df):
    returns = np.array(returns)
    win_rate = np.mean(returns > 0) * 100 if len(returns) > 0 else 0
    avg_gain = np.mean(returns[returns > 0]) * 100 if np.any(returns > 0) else 0
    avg_loss = np.mean(returns[returns < 0]) * 100 if np.any(returns < 0) else 0
    total_return_pct = (equity_df['equity'].iloc[-1] - equity_df['equity'].iloc[0]) / equity_df['equity'].iloc[0] * 100

    equity_df['daily_return'] = equity_df['equity'].pct_change().dropna()
    sharpe_ratio = (equity_df['daily_return'].mean() / equity_df['daily_return'].std()) * np.sqrt(252) if equity_df['daily_return'].std() != 0 else 0

    cum_max = equity_df['equity'].cummax()
    drawdown = (equity_df['equity'] - cum_max) / cum_max
    max_drawdown = drawdown.min() * 100

    return {
        "Total Return (%)": round(total_return_pct, 2),
        "Win Rate (%)": round(win_rate, 2),
        "Avg Gain (%)": round(avg_gain, 2),
        "Avg Loss (%)": round(avg_loss, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown, 2)
    }

# ------------------ Backtest Logic ------------------
def backtest(df):
    capital = 100000
    position = 0
    entry_price = 0
    equity_curve = []
    trades = []

    for i in range(1, len(df)):
        row_today = df.iloc[i]
        price = row_today['Close']

        supertrend_signal = row_today['Close'] > row_today['SUPERTREND']
        supertrend_bear = row_today['Close'] < row_today['SUPERTREND']
        above_vwap = row_today['Close'] > row_today['VWAP']
        beLow_vwap = row_today['Close'] < row_today['VWAP']
        macd_bull = row_today['MACD'] > row_today['MACD_signal']
        macd_bear = row_today['MACD'] < row_today['MACD_signal']

        if position == 0 and supertrend_signal and above_vwap and macd_bull:
            position = capital / price
            entry_price = price
            capital = 0
            trades.append({'type': 'BUY', 'price': price, 'datetime': row_today.name})

        elif position > 0 and supertrend_bear and beLow_vwap and macd_bear:
            capital = position * price
            trades.append({'type': 'SELL', 'price': price, 'datetime': row_today.name})
            position = 0

        equity = capital if position == 0 else position * price
        equity_curve.append({'datetime': row_today.name, 'equity': equity})

    equity_df = pd.DataFrame(equity_curve).set_index('datetime')
    final_equity = equity_df['equity'].iloc[-1]
    trades_df = pd.DataFrame(trades)

    returns = []
    for i in range(1, len(trades), 2):
        buy = trades[i-1]
        sell = trades[i]
        if buy['type'] == 'BUY' and sell['type'] == 'SELL':
            pct_return = (sell['price'] - buy['price']) / buy['price']
            returns.append(pct_return)

    metrics = calculate_performance_metrics(returns, equity_df)
    return final_equity, trades_df, equity_df, metrics

# ------------------ Plot Equity Curve ------------------
def plot_equity_curve(equity_df, trades_df):
    plt.figure(figsize=(14, 6))
    plt.plot(equity_df.index, equity_df['equity'], label='Equity Curve', color='blue')
    for _, trade in trades_df.iterrows():
        if trade['type'] == 'BUY':
            plt.axvline(x=trade['datetime'], color='green', linestyle='--', alpha=0.4)
        elif trade['type'] == 'SELL':
            plt.axvline(x=trade['datetime'], color='red', linestyle='--', alpha=0.4)
    plt.title('Equity Curve with Trade Points')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value (₹)')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

# ------------------ Run Backtest ------------------
if __name__ == "__main__":
    df = pd.read_csv('RELIANCE.NS.csv',parse_dates=['timestamp'],skiprows=[1])  # Replace with your file path
    # df = load_data('RELIANCE.NS')
    df = add_indicators(df)

    final_equity, trades_df, equity_df, metrics = backtest(df)

    print(f"\n📈 Initial: ₹100,000 → Final: ₹{final_equity:,.2f}")
    print(f"🔁 Total Trades: {len(trades_df) // 2}")
    print(trades_df.tail())

    print("\n📊 Performance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    plot_equity_curve(equity_df, trades_df)
