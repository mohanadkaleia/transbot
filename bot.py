import websocket
import json
import sheet
import datetime
import time
from slacker import Slacker


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
            raise InvalidBot(f"Bot with name {self.name} is not found")

        return self.users[self.name]

    def connect(self):
        # Check for success
        if self.client.api.test().successful:
            print(
                f"{self.name} Connected to {self.client.team.info().body['team']['name']}."
            )
        else:
            raise ConnectionFailed("Connection failed please try again!")

    def handle(self, event):
        event = json.loads(event)

        if event["type"] != "message":
            return

        if event.get("text", "").startswith(f"<@{self.user['id']}>"):
            message = event["text"].replace(f"<@{self.user['id']}>", "")
            self.exec_command(event["channel"], event["user"], message.strip())

    def exec_command(self, channel, user_id, raw_message):
        if raw_message.startswith("help") or raw_message.startswith("/help"):
            self.help(channel)
        elif raw_message.startswith("/pending"):
            self.pending(channel)
        else:
            for term in self.sheet.all():
                if raw_message in term["English"]:
                    self.post_message(
                        channel, f"Seems {raw_message} is already in the dictionary."
                    )
                    if term["Arabic"]:
                        self.post_message(
                            channel, f"Here is its translation {term['Arabic']}"
                        )
                        return

            author = self.users[user_id]
            row = [raw_message, "", "", author["name"], str(datetime.datetime.today())]
            self.sheet.insert(row)
            self.post_message(channel, f"Yay! I added the term '{raw_message}'")

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
                print(e)
                print("Oh oh.. something went wrong.. trying in 3 sec..")
                time.sleep(3)

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
                            "text": f"{i}: *{term['English']}*",
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
            "Hey there 👋 I'm Transbot. I'm here to notify you about terms that still need a translation.\nHere is a list of all pending terms:",
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

