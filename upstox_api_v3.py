from dotenv import load_dotenv
import os
import requests

load_dotenv()
def get_intraday_v3(intrumment_key,interval=1,interval_type='minutes'):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    url = f'https://api.upstox.com/v3/historical-candle/intraday/{intrumment_key}/{interval_type}/{interval}'
    headers = {
        'Accept': 'application/json',
        'Authorization':f'Bearer {ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        return response.json()
    else: 
        print(f"Error: {response.status_code} - {response.text}")
        return response.json()