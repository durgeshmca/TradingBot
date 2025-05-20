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
from ai.openai_lib import get_market_explanation
from trade_logger import init_db, log_trade_to_db
from upstox_api_v3 import get_intraday_v3
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


# Store last executed order
active_trade = {
    "type": 'BUY',
    "entry_price": 1559.8,
    "stop_loss": 1544.2,
    "target": 1575.3
}
# Fetch historical data
# def fetch_data():
#     candles = u.get_ohlc(INSTRUMENT_TOKEN, OHLCInterval.Minute_15, 50)
#     df = pd.DataFrame(candles)
#     df['close'] = df['close'].astype(float)
#     return df
def get_ltp(instrument_key):
    try:
        api_version = '2.0'
        api_instance = upstox_client.MarketQuoteApi(api_client)
        api_response = api_instance.ltp(instrument_key,api_version)
        ltp = api_response.data
        # print(ltp[list(ltp.keys())[0]].last_price)
        # # raise Exception('Error')
        return ltp[list(ltp.keys())[0]].last_price
       
    except Exception as e:
        print("Exception when calling MarketQuoteApi-> MarketQuoteApi :%s\n" % e)

def fetch_data():
    try:
    # Historical candle data
    # intraday
        # api_response=api_instance.get_intra_day_candle_data(instrument_key=instrument_key,interval='1minute',api_version=api_version)
        # # api_response = api_instance.get_historical_candle_data(instrument_key, interval, to_date, api_version)
        # # api_response.keys()
        # # print(api_response.data)
        
        
        # if api_response.status=='success':
        #     response_data = api_response.data
        #     candles = response_data.candles
        #     df = pd.DataFrame(candles,columns=['timestamp','open','high','low','close','volume','other'])
        #     df['close'] = df['close'].astype(float)
        #     df = df.sort_values(by=['timestamp'],ascending=True)
        #     return df
    # Adding version 3 api of upstox
        intraday_data = get_intraday_v3(instrument_key,2,'minutes')
        if intraday_data.get('status',None) == 'success':
            df = pd.DataFrame(intraday_data['data']['candles'],columns=['timestamp','open','high','low','close','volume','open_interest'])
            df['close'] = df['close'].astype(float)
            return df

    except Exception as e:
        print("Exception when calling HistoryApi->get_historical_candle_data1: %s\n" % e)


def place_order(signal,price,current_volume=0,average_volume=0):
    global active_trade
    try:
        # response = u.place_order(
        #     transaction_type=u.TransactionType.Buy if signal == 'BUY' else u.TransactionType.Sell,
        #     instrument=u.get_instrument_by_token(EXCHANGE, INSTRUMENT_TOKEN),
        #     quantity=1,
        #     order_type=u.OrderType.Market,
        #     product=u.ProductType.MIS,
        #     duration=u.Duration.DAY
        # )
       
        # get current market price
        ltp = get_ltp(instrument_key=instrument_key)
        print('Last traded price',ltp)
        ########################LLM INsights ################################
        explanation = get_market_explanation(
            signal_type=signal,
            symbol='INFOSYS',
            ltp=ltp,
            trend='uptrend' if signal=='BUY' else 'downtrend',
            volume='above average' if current_volume> average_volume else 'below average',
        )

        print("\n📣 GPT Market Insight:")
        print(explanation)
        send_telegram_alert("🧠 GPT Insight:\n" + explanation)
        ########################################################
        entry_price = ltp
        stop_loss = entry_price * 0.99  # 1% SL
        target = entry_price * 1.01     # 1% Target
        message = f"✅ crossover detected {signal} {instrument_key} at {price} "
        active_trade = {
            "type": signal,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target
        }
        print(message)
        print(f"{signal} Order Placed @ ₹{entry_price}| SL: ₹{stop_loss}, Target: ₹{target}")
        
        log_trade_to_db(signal,instrument_key)  # log trade
        send_telegram_alert(f"{message}. \n {signal} Order Placed @ ₹{entry_price} | SL: ₹{stop_loss}, Target: ₹{target}")
    except Exception as e:
        print(f"❌ Error placing order: {e}")
        send_telegram_alert(f"Order Failed: {e}")


def monitor_trade():
    global active_trade
    if active_trade["type"]:
        # get last traded price
       
        ltp = get_ltp(instrument_key=instrument_key)

        if active_trade["type"] == "BUY":
            if ltp <= active_trade["stop_loss"]:
                print("❌ Stop Loss Hit. Exit Position.")
                send_telegram_alert("❌ SL Hit. Exit Position.")
                active_trade = {"type": None, "entry_price": None, "stop_loss": None, "target": None}
            elif ltp >= active_trade["target"]:
                print("✅ Target Achieved. Exit Position.")
                send_telegram_alert("✅ Target Achieved. Exit Position.")
                active_trade = {"type": None, "entry_price": None, "stop_loss": None, "target": None}


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
    average_volume  = df['volume'].mean()
    current_volume = df['volume'].iloc[-1]
    if signal == 'BUY':
        print(f"💰 Buy 1 unit of {SYMBOL}")
        place_order(signal,df['close'].iloc[-1],current_volume,average_volume)

    elif signal == 'SELL':
        print(f"💸 Sell 1 unit of {SYMBOL}")
        place_order(signal,df['close'].iloc[-1],current_volume,average_volume)


# Schedule the bot every 15 minutes
schedule.every(2).minutes.at(":00").do(moving_average_strategy)
schedule.every(1).minutes.do(monitor_trade)

print("📈 Starting live bot... (CTRL+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(1)
