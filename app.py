import bot
import sheet
import os


token = os.environ["SLACK_BOT_TOKEN"]
sheet_url = os.environ["SHEET_URL"]
# sheet = sheet.Sheet(sheet_url)
# print(sheet.get_untranslated_terms())
bot = bot.Bot("transbot", token, sheet_url)

