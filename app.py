import bot
import os


token = os.environ["SLACK_BOT_TOKEN"]
sheet_url = "https://docs.google.com/spreadsheets/d/1B_n1GrhvGYEK8_mrhLnUURT5u_eSaxIXB6l7PmmYZmQ"

bot = bot.Bot("transbot", token)

