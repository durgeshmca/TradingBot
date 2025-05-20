import os
from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
# Scrip details
EXCHANGE = 'NSE_EQ'
SYMBOL = 'INFOSYS'
INSTRUMENT_TOKEN = '2885'  # Reliance NSE token
