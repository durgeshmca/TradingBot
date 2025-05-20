import openai
import os
from dotenv import load_dotenv
load_dotenv()
# from ..config import OPENAI_TOKEN
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
# openai.api_key = OPENAI_TOKEN
import datetime

client = openai.OpenAI(api_key=OPENAI_TOKEN)

def get_market_explanation(signal_type, symbol, ltp, trend="sideways", volume="normal"):
    prompt = f"""
You are a financial trading assistant.

A {signal_type.upper()} signal was generated for {symbol} at price ₹{ltp}.

The recent market trend is: {trend}.
Trading volume is: {volume}.

Explain in plain English:
- Why this might be a good signal
- What the trader should watch for
- Any caution or risk
    """
    
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        temperature=0.6
        
    )
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.6
    # )
    
    explanation = response.output_text.strip()
    return explanation

######################## Generate GPT Insight #########################

def generate_gpt_insights(symbol, signal_type, ltp, rsi, bb_upper, bb_lower, close_price,
                          news_list=None, events_list=None):
    news_text = "\n".join([f"{i+1}. {n}" for i, n in enumerate(news_list)]) if news_list else "No major news today."
    events_text = "\n".join([f"{i+1}. {e}" for i, e in enumerate(events_list)]) if events_list else "No major events scheduled."

    today = datetime.datetime.now().strftime("%d %b %Y")

    prompt = f"""
        You are a professional financial market assistant. Analyze the following for {symbol}:

        📅 Date: {today}
        📉 A {signal_type.upper()} signal was generated at ₹{ltp}.
        📊 Technicals:
        - RSI = {rsi:.2f}
        - Bollinger Bands: Upper = ₹{bb_upper:.2f}, Lower = ₹{bb_lower:.2f}, Price = ₹{close_price:.2f}

        📰 Recent News Headlines:
        {news_text}

        📆 Upcoming Events:
        {events_text}

        Please answer:
        1. What does the signal suggest?
        2. Is the RSI or Bollinger Band signaling anything?
        3. How does news affect this signal?
        4. What to watch for in upcoming events?
        5. Final recommendation (Bullish, Bearish, or Neutral) with caution if any.
        """

    try:
        response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        temperature=0.6
        
    )
        return response.output_text.strip()
    except Exception as e:
        return f"❌ GPT Error: {str(e)}"
    

    ################### test #########################

if __name__ == "__main__":
    symbol = "RELIANCE"
    signal_type = "BUY"
    ltp = 2500
    rsi = 64.5
    bb_upper = 2520
    bb_lower = 2450
    close_price = 2500

    news_list = [
        "Reliance Q4 profit beats expectations led by Jio growth",
        "Retail business expands 20% YoY",
        "Oil-to-chem margins remain under pressure"
    ]

    events_list = [
        "RBI rate decision on May 22",
        "Reliance earnings call on May 26"
    ]

    insight = generate_gpt_insights(symbol, signal_type, ltp, rsi, bb_upper, bb_lower, close_price, news_list, events_list)

    print(insight)
