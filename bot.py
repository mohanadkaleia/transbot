import websocket
import json
import sheet
import datetime
import time
import logger
from slacker import Slacker

log = logger.get_logger(__name__)


class InvalidBot(Exception):
    pass


class ConnectionFailed(Exception):
    pass


class Bot:
    def __init__(self, name, token, sheet_url):
        self.name = name
        self.client = Slacker(token)
        self.connect()
        self.sheet = sheet.Sheet(sheet_url)
        self.users = {}
        self.user = self.get_user()
        self.run()

    def get_user(self):
        if not self.users:
            for user in self.client.users.list().body["members"]:
                self.users[user["id"]] = user
                self.users[user["name"]] = user

        if self.name not in self.users:
            raise InvalidBot("Bot with name %s is not found"  % (self.name))

        return self.users[self.name]

    def connect(self):
        # Check for success
        if self.client.api.test().successful:
            print("%s Connected to %s." %(self.name, self.client.team.info().body['team']['name']))
            log.info("Bot has been connected successfully")
        else:
            log.error("Could not connect with Slack API")
            raise ConnectionFailed("Connection failed please try again!")

    def handle(self, event):
        event = json.loads(event)

        if event["type"] != "message":
            return

        if event.get("text", "").startswith("<@%s>" % (self.user['id'])):            
            message = event["text"].replace("<@%s>" % (self.user['id']), "")
            self.exec_command(event["channel"], event["user"], message.strip())

    def exec_command(self, channel, user_id, raw_message):
        if raw_message.startswith("help") or raw_message.startswith("/help"):
            log.info("Received help command")
            self.help(channel)
        elif raw_message.startswith("/pending"):
            log.info("Received pending command")
            self.pending(channel)
        elif raw_message.startswith("/all"):
            log.info("Received pending command")
            self.all(channel)
        else:
            log.info("Received term %s" % (raw_message))
            
            # Clean up non-English letters
            raw_message = clean(raw_message)

            for term in self.sheet.all():
                if raw_message.lower() in term["English"].lower():                    
                    if term["Arabic"]:
                        self.post_message(
                            channel, "`%s`: `%s` 🤓" %(term["English"], term['Arabic'])
                        )                          
                    else:
                        self.post_message(channel, "`%s` already exist in the dictionary and pending translation." % (raw_message))
                    return

            author = self.users[user_id]
            row = [raw_message, "", "", author["name"], str(datetime.datetime.today())]
            self.sheet.insert(row)
            self.post_message(channel, "✅ `%s` has been added!" % (raw_message))

    def post_message(self, channel, message, attachment=None):
        self.client.chat.post_message(
            channel=channel, text=message, attachments=attachment
        )

    def upload(self, file, title, comment, channel):
        self.client.files.upload(
            file_=file, channels=[channel], title=title, initial_comment=comment
        )

    def run(self):
        while True:
            try:
                rtm = self.client.rtm.start()
                url = rtm.body["url"]
                ws = websocket.WebSocket()
                ws.connect(url)
                while True:
                    message = ws.recv()
                    self.handle(message)
            except Exception as e:
                log.error(e)
                print("Oh oh.. something went wrong.. trying in 3 sec..")
                time.sleep(3)

    def all(self, channel):
        message = {"blocks": []}

        terms = self.sheet.all()
        if not terms:
            message["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hmmm.. the dictionary is empty.. that is weird!",
                    },
                },
            )
        else:
            for term in terms:
                message["blocks"].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "`%s` -> `%s`" % (term['English'], term['Arabic']),
                        },
                    },
                )
            message["blocks"].append(
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "image1", "emoji": True},
                    "image_url": "https://media.giphy.com/media/o5oLImoQgGsKY/200w_d.gif",
                    "alt_text": "image1",
                }
            )

        self.post_message(
            channel,
            "Here is a list of all terms in the dictionary including the pending ones 😇.\n:",
            [message],
        )


    def pending(self, channel):
        message = {"blocks": []}

        terms = self.sheet.get_untranslated_terms()
        if not terms:
            message["blocks"].append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Yay!! all terms are translated so far!! whooray!",
                    },
                },
            )
        else:
            for i, term in enumerate(terms, 1):
                message["blocks"].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "%s: `%s`" % (i, term['English']),
                        },
                    },
                )
            message["blocks"].append(
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "image1", "emoji": True},
                    "image_url": "https://media.giphy.com/media/o5oLImoQgGsKY/200w_d.gif",
                    "alt_text": "image1",
                }
            )

        self.post_message(
            channel,
            "Here is a list of all pending terms: 👻",
            [message],
        )

    def help(self, channel):
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Hey there 👋 I'm Transbot. I'm here to help you create and manage terms in the field of AI in Slack.\n Here is what I can do:",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*1️⃣ Use the `/pending` command*. Mention me and then type `/pending`, and I will list all terms that are pending translation.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*2️⃣ Add new term to the dictionary.* If you want to add a new term to the dictionary just mention my name followed by the term you want to add. Example: `[at]transbot science` if the term exists in the dictionary I will return its translation other wise I will just add it happily to the dicrtionary",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*3️⃣ Use the `/help` command*. Mention me and then type `/help`, and I will help you as much as I can 🥴.",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*4️⃣ Use the `/all` command*. this command returns all terms in the dictionary including the pending ones 🤓.",
                    },
                },
                {
                    "type": "image",
                    "title": {"type": "plain_text", "text": "image1", "emoji": True},
                    "image_url": "https://media.giphy.com/media/WxIn3PAoXHqZWbR6eg/200w_d.gif",
                    "alt_text": "image1",
                },
                {"type": "divider"},
            ]
        }        
        self.post_message(
            channel, "", [message],
        )

    
def clean(message):
    words = message.split(' ')
    l = []
    for word in words:
        l.append(''.join(letter for letter in word.lower() if 'a' <= letter <= 'z'  or letter.isdigit()))
    
    return ' '.join(l).strip()

