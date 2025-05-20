from __future__ import print_function
import time
import schedule
import numpy as np
import pandas as pd
from datetime import datetime
import upstox_client
from upstox_client.rest import ApiException
from telegram import send_telegram_alert
# from upstox_api.api import Upstox, OHLCInterval
from config import API_KEY, API_SECRET, REDIRECT_URI, INSTRUMENT_TOKEN, SYMBOL, EXCHANGE,ACCESS_TOKEN
from trade_logger import init_db, log_trade_to_db
init_db()

configuration = upstox_client.Configuration(sandbox=False)
configuration.access_token = ACCESS_TOKEN
api_client = upstox_client.ApiClient(configuration)

api_instance = upstox_client.HistoryApi(api_client)
instrument_key = 'NSE_EQ|INE009A01021' # str | 
interval = '1minute' # str | 
to_date = '2025-05-15' # str | 
from_date = '2025-05-15' # str | 
api_version = 'v3' # str | API Version Header


# Fetch historical data
# def fetch_data():
#     candles = u.get_ohlc(INSTRUMENT_TOKEN, OHLCInterval.Minute_15, 50)
#     df = pd.DataFrame(candles)
#     df['close'] = df['close'].astype(float)
#     return df
import requests
def get_intraday_v3(interval=1,interval_type='minutes'):

    url = 'https://api.upstox.com/v3/historical-candle/intraday/NSE_EQ%7CINE848E01016/minutes/1'
    headers = {
        'Accept': 'application/json',
        'Authorization':f'Bearer {ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        # Do something with the response data (e.g., print it)
        return response.json()
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")

def fetch_data():
    try:
    # Historical candle data
    # intraday
        api_response=api_instance.get_intra_day_candle_data(instrument_key=instrument_key,interval='1minute',api_version=api_version)
        # api_response = api_instance.get_historical_candle_data(instrument_key, interval, to_date, api_version)
        # api_response.keys()
        # print(api_response.data)
        
        
        if api_response.status=='success':
            response_data = api_response.data
            candles = response_data.candles
            df = pd.DataFrame(candles,columns=['timestamp','open','high','low','close','volume','other'])
            df['close'] = df['close'].astype(float)
            df = df.sort_values(by=['timestamp'],ascending=True)
            return df

    except Exception as e:
        print("Exception when calling HistoryApi->get_historical_candle_data1: %s\n" % e)


def place_order(signal,price):
    try:
        # response = u.place_order(
        #     transaction_type=u.TransactionType.Buy if signal == 'BUY' else u.TransactionType.Sell,
        #     instrument=u.get_instrument_by_token(EXCHANGE, INSTRUMENT_TOKEN),
        #     quantity=1,
        #     order_type=u.OrderType.Market,
        #     product=u.ProductType.MIS,
        #     duration=u.Duration.DAY
        # )
        message = f"✅ crossover detected {signal} {instrument_key} at {price} "
        print(message)
        log_trade_to_db(signal,instrument_key)  # log trade
        send_telegram_alert(f"{message}")
    except Exception as e:
        print(f"❌ Error placing order: {e}")
        send_telegram_alert(f"Order Failed: {e}")


# Strategy: MA Crossover
def moving_average_strategy():
    df = fetch_data()
    df['SMA20'] = df['close'].rolling(20).mean()
    df['SMA50'] = df['close'].rolling(50).mean()
    print(df['timestamp'].iloc[-1])
    print('SMA20',df['SMA20'].iloc[-1])
    print('SMA50',df['SMA50'].iloc[-1])
    print('Current Price',df['close'].iloc[-1])
    signal = None

    if df['SMA20'].iloc[-2] < df['SMA50'].iloc[-2] and df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
        signal = 'BUY'
    elif df['SMA20'].iloc[-2] > df['SMA50'].iloc[-2] and df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
        signal = 'SELL'
    # if  df['SMA20'].iloc[-1] > df['SMA50'].iloc[-1]:
    #     signal = 'BUY'
    # elif df['SMA20'].iloc[-1] < df['SMA50'].iloc[-1]:
    #     signal = 'SELL'

    print(f"{datetime.now()} — Signal: {signal}")
    
    # Simulate placing an order (paper trading)
    if signal == 'BUY':
        print(f"💰 Buy 1 unit of {SYMBOL}")
        place_order(signal,df['close'].iloc[-1])

    elif signal == 'SELL':
        print(f"💸 Sell 1 unit of {SYMBOL}")
        place_order(signal,df['close'].iloc[-1])


# Schedule the bot every 15 minutes
schedule.every(1).minutes.at(":00").do(moving_average_strategy)

print("📈 Starting live bot... (CTRL+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(1)
