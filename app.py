import bot
import sheet
import os
import logger

log = logger.get_logger(__name__)

token = os.environ["SLACK_BOT_TOKEN"]
sheet_url = os.environ["SHEET_URL"]
While True: 
    try:
        bot = bot.Bot("transbot", token, sheet_url)
    except Exception as e:
        log.exception(e)

