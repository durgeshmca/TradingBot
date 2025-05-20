import pandas as pd
import pandas_ta as ta

def add_indicators(df):
    df['RSI'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    return df

def check_rsi_macd_signal(df):
    if len(df) < 2:
        return None

    rsi_prev, rsi_now = df['RSI'].iloc[-2], df['RSI'].iloc[-1]
    macd_prev, macd_now = df['MACD'].iloc[-2], df['MACD'].iloc[-1]
    signal_prev, signal_now = df['MACD_signal'].iloc[-2], df['MACD_signal'].iloc[-1]

    # Buy Condition
    if rsi_prev < 50 and rsi_now > 50 and macd_prev < signal_prev and macd_now > signal_now:
        return "BUY"
    
    # Sell Condition
    elif rsi_prev > 50 and rsi_now < 50 and macd_prev > signal_prev and macd_now < signal_now:
        return "SELL"
    
    return None

if __name__ == "__main__":
    df = get_ohlcv_data("RELIANCE", interval="15minute", days=5)  # use your fetch function
    df = add_indicators(df)

    signal = check_rsi_macd_signal(df)
    if signal:
        print(f"✅ Combined RSI + MACD Signal: {signal}")
        # trigger order or explain via GPT
    else:
        print("No signal yet.")
