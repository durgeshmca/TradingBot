import pandas_ta as ta
import pandas as pd
def add_indicators(df):
    df['RSI'] = ta.rsi(df['close'], length=14)

    macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']

    supertrend = ta.supertrend(df['high'], df['low'], df['close'], length=20, multiplier=2.0)
    df['SUPERTREND'] = supertrend['SUPERT_20_2.0']

    df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

    return df.dropna()
