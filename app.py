import bot
import os


token = os.environ["SLACK_BOT_TOKEN"]
bot = bot.Bot("transbot", token)

