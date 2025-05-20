import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def load_data(symbol):
    # symbol = 'RELIANCE.NS'
    df = yf.download(symbol, start="2022-01-01", end="2025-05-15")
    df = df.reset_index()
    print(df.columns)
    # df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    df['timestamp']= df['Date']
    df = df.sort_values('timestamp')
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df.to_csv(f'{symbol}.csv')
    return df

def backtest_ma_crossover(df):
    buy_price = 0
    position = False
    returns = []
    for i in range(1, len(df)):
        if df['SMA20'].iloc[i-1] < df['SMA50'].iloc[i-1] and df['SMA20'].iloc[i] > df['SMA50'].iloc[i]:
            # Buy
            buy_price = df['Close'].iloc[i]
            position = True
            df.at[df.index[i], 'signal'] = 'BUY'

        elif position and df['SMA20'].iloc[i-1] > df['SMA50'].iloc[i-1] and df['SMA20'].iloc[i] < df['SMA50'].iloc[i]:
            # Sell
            sell_price = df['Close'].iloc[i]
            ret = (sell_price - buy_price) / buy_price
            returns.append(ret)
            df.at[df.index[i], 'signal'] = 'SELL'
            position = False

    return returns, df

def plot_chart(df):
    plt.figure(figsize=(14, 6))
    plt.plot(df['timestamp'], df['Close'], label='Close Price')
    plt.plot(df['timestamp'], df['SMA20'], label='SMA20', linestyle='--')
    plt.plot(df['timestamp'], df['SMA50'], label='SMA50', linestyle='--')
    plt.scatter(df[df['signal'] == 'BUY']['timestamp'], df[df['signal'] == 'BUY']['Close'], label='Buy', marker='^', color='green')
    plt.scatter(df[df['signal'] == 'SELL']['timestamp'], df[df['signal'] == 'SELL']['Close'], label='Sell', marker='v', color='red')
    plt.legend()
    plt.title('Moving Average Crossover Backtest')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def summary_stats(returns):
    total_trades = len(returns)
    wins = 0
    print('returns',returns)
    for r in returns:
        print(r)
        if r> 0:
            wins += 1
    # wins = sum(1 for r in returns if r > 0)
    losses = total_trades - wins
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0
    cumulative_return = (1 + pd.Series(returns)).prod() - 1

    print("\n📊 Backtest Summary")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Cumulative Return: {cumulative_return*100:.2f}%")
    print(f"Avg Return per Trade: {pd.Series(returns).mean(numeric_only=True)*100:.2f}%")

if __name__ == "__main__":
    # path = "historical_data.csv"  # CSV file with columns: timestamp, open, high, low, close, volume
    symbol = 'MSUMI.NS'
    # df = load_data(symbol)
    df = pd.read_csv('MSUMI.NS.csv',parse_dates=['timestamp'],skiprows=[1])
    print(df)
    returns, df = backtest_ma_crossover(df)
    print(returns)
    print(df)
    if len(returns)> 0:
        summary_stats(returns)
        plot_chart(df)
    else :
        print('No trade executed')
