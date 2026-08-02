import os
import requests
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

message = """
📈 NEPSE Scanner

Bot is running ✅

Market scan will be added soon.
"""

bot.send_message(chat_id=CHAT_ID, text=message)
