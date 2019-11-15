import bot
import sheet
import os
import logger
import config

log = logger.get_logger(__name__)

token = config.prod['slack_token']
sheet_url = config.prod["sheet"]

while True:
    try:
        bot = bot.Bot("transbot", token, sheet_url)
    except Exception as e:
        log.exception(e)
