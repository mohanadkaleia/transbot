import bot
import os


token = os.environ["SLACK_BOT_TOKEN"]
sheet_url = os.environ["SHEET_URL"]

bot = bot.Bot("transbot", token, sheet_url)

