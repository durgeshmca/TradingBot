import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np

def load_data(filepath):
    df = pd.read_csv(filepath, parse_dates=['datetime'])
    df = df.sort_values('datetime')
    df = df.set_index('datetime')
    return df

def add_indicators(df):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    return df.dropna()

def calculate_performance_metrics(returns, equity_df):
    returns = np.array(returns)
    win_rate = np.mean(returns > 0) * 100 if len(returns) > 0 else 0
    avg_gain = np.mean(returns[returns > 0]) * 100 if np.any(returns > 0) else 0
    avg_loss = np.mean(returns[returns < 0]) * 100 if np.any(returns < 0) else 0
    total_return_pct = (equity_df['equity'].iloc[-1] - equity_df['equity'].iloc[0]) / equity_df['equity'].iloc[0] * 100

    # Daily returns for Sharpe Ratio
    equity_df['daily_return'] = equity_df['equity'].pct_change().dropna()
    sharpe_ratio = (equity_df['daily_return'].mean() / equity_df['daily_return'].std()) * np.sqrt(252) if equity_df['daily_return'].std() != 0 else 0

    # Max Drawdown
    cum_max = equity_df['equity'].cummax()
    drawdown = (equity_df['equity'] - cum_max) / cum_max
    max_drawdown = drawdown.min() * 100  # in %

    return {
        "Total Return (%)": round(total_return_pct, 2),
        "Win Rate (%)": round(win_rate, 2),
        "Avg Gain (%)": round(avg_gain, 2),
        "Avg Loss (%)": round(avg_loss, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2),
        "Max Drawdown (%)": round(max_drawdown, 2)
    }


def backtest(df, initial_capital=100000):
    position = 0
    entry_price = 0
    capital = initial_capital
    equity_curve = []
    trades = []

    for i in range(1, len(df)):
        row_yesterday = df.iloc[i - 1]
        row_today = df.iloc[i]

        rsi_cross_up = row_yesterday['RSI'] < 50 and row_today['RSI'] > 50
        macd_cross_up = row_yesterday['MACD'] < row_yesterday['MACD_signal'] and row_today['MACD'] > row_today['MACD_signal']
        rsi_cross_down = row_yesterday['RSI'] > 50 and row_today['RSI'] < 50
        macd_cross_down = row_yesterday['MACD'] > row_yesterday['MACD_signal'] and row_today['MACD'] < row_today['MACD_signal']

        price = row_today['Close']

        if position == 0:
            if rsi_cross_up and macd_cross_up:
                position = capital / price
                entry_price = price
                capital = 0
                trades.append({'type': 'BUY', 'price': price, 'datetime': row_today.name})
        else:
            if rsi_cross_down and macd_cross_down:
                capital = position * price
                trades.append({'type': 'SELL', 'price': price, 'datetime': row_today.name})
                position = 0

        current_value = capital + (position * price)
        equity_curve.append({'datetime': row_today.name, 'equity': current_value})

    if position > 0:
        capital = position * df.iloc[-1]['Close']
        trades.append({'type': 'SELL', 'price': df.iloc[-1]['Close'], 'datetime': df.iloc[-1].name})
        position = 0

    final_equity = capital
    equity_df = pd.DataFrame(equity_curve).set_index('datetime')
    trades_df = pd.DataFrame(trades)
    returns = []
    for i in range(1, len(trades), 2):  # every buy/sell pair
        buy = trades[i-1]
        sell = trades[i]
        if buy['type'] == 'BUY' and sell['type'] == 'SELL':
            pct_return = (sell['price'] - buy['price']) / buy['price']
            returns.append(pct_return)
    metrics = calculate_performance_metrics(returns, equity_df)
    return final_equity, trades_df, equity_df, metrics

def plot_equity_curve(equity_df):
    plt.figure(figsize=(12, 6))
    plt.plot(equity_df.index, equity_df['equity'], label='Equity Curve')
    plt.title("Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Capital")
    plt.grid()
    plt.legend()
    plt.show()

# Example Usage
if __name__ == "__main__":
    df = pd.read_csv('reliance.csv',parse_dates=['timestamp'],skiprows=[1])  # your OHLCV file with 'datetime','open','high','low','Close','volume'
    df = add_indicators(df)
    final_equity, trades_df, equity_df, metrics = backtest(df) 

    print(f"\n📈 Initial: ₹100,000 → Final: ₹{final_equity:,.2f}")
    print(f"🔁 Total Trades: {len(trades_df)//2}")
    print(trades_df.tail())

    print("\n📊 Performance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    plot_equity_curve(equity_df)
