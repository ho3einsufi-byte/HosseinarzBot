import os
import telebot
import pandas as pd
import mplfinance as mpf
import requests
from io import BytesIO
import matplotlib.pyplot as plt

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telebot.TeleBot(TOKEN)

def fetch_ohlcv(symbol="BTCUSDT", interval="1h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "", "", "", "", "", ""])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)
    return df[["open", "high", "low", "close", "volume"]]

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, "سلام! برای دریافت تحلیل چارت، دستور /chart BTCUSDT را وارد کن.")

@bot.message_handler(commands=["chart"])
def send_chart(message):
    try:
        parts = message.text.split()
        symbol = parts[1].upper() if len(parts) > 1 else "BTCUSDT"
        df = fetch_ohlcv(symbol)
        fig, ax = plt.subplots()
        mpf.plot(df.tail(50), type='candle', mav=(3,6,9), volume=True, ax=ax, style='charles')
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        bot.send_photo(message.chat.id, buf, caption=f"چارت {symbol}")
    except Exception as e:
        bot.reply_to(message, f"خطا در گرفتن چارت: {e}")

bot.infinity_polling()