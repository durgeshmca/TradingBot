import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import upstox_client
# from ma_crossover_bot import get_ltp
# from upstox_api.api import Upstox
from config import API_KEY, API_SECRET, INSTRUMENT_TOKEN, ACCESS_TOKEN

# ACCESS_TOKEN = 'your_access_token_here'

# Connect to Upstox
# u = Upstox(API_KEY, API_SECRET)
# u.set_access_token(ACCESS_TOKEN)
# print(ACCESS_TOKEN)
configuration = upstox_client.Configuration(sandbox=False)
configuration.access_token = ACCESS_TOKEN
api_client = upstox_client.ApiClient(configuration)
instrument_key = 'NSE_EQ|INE009A01021' # str | 

# Get Live Price
def get_ltp(instrument_key):
    try:
        api_version = '2.0'
        api_instance = upstox_client.MarketQuoteApi(api_client)
        api_response = api_instance.ltp(instrument_key,api_version)
        # print(api_response)
        ltp = api_response.data
        print(ltp[list(ltp.keys())[0]].last_price)
        # raise Exception('Error')
        return ltp[list(ltp.keys())[0]].last_price
    except Exception as e:
        print(f'Error:{e}')
        return None


# Read trades from SQLite
def fetch_trade_history():
    conn = sqlite3.connect('db/trades.db')
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY datetime DESC", conn)
    conn.close()
    return df

# Active trade display (simulate - you can link it to a DB later)
def get_active_trade():
    # For now, assume a dummy open position
    return {
        "type": "BUY",
        "entry_price": 2500,
        "stop_loss": 2475,
        "target": 2525
    }

# Streamlit UI
st.set_page_config(page_title="Algo Trading Dashboard", layout="centered")
st.title("📈 Algo Trading Dashboard")

st.header("🔁 Live Price")
price = get_ltp(instrument_key)
if price:
    st.metric(label="Current Price", value=f"₹{price:.2f}")
else:
    st.warning("Unable to fetch live price.")

# Show Active Trade
st.header("📌 Open Position")
active = get_active_trade()
if active["type"]:
    st.write(f"**Type:** {active['type']}")
    st.write(f"**Entry:** ₹{active['entry_price']}")
    st.write(f"**Stop Loss:** ₹{active['stop_loss']}")
    st.write(f"**Target:** ₹{active['target']}")
else:
    st.info("No open trades.")

# Trade history
st.header("📜 Trade History")
df = fetch_trade_history()
st.dataframe(df)

st.caption("Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
