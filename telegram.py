import requests
import os
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        res= requests.post(url, data=payload)
        print(res.text)
    except Exception as e:
        print(f"Telegram error: {e}")

if __name__ == '__main__':
    send_telegram_alert('Hello, Friends!')