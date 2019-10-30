import websocket
import json
import sheet
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
        self.user = self.get_user()
        self.run()

    def get_user(self):
        for user in self.client.users.list().body["members"]:
            if user["name"] == self.name:
                return user

        if not self.user:
            raise InvalidBot(f"Bot with name {self.name} is not found")

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
            # TODO:
            # 1. Read the excel file and return the term in case it is there
            # 2. Add it to the Excel sheet in case it is not there
            # 3. Return a message that the term has been added
            self.post_message(event["channel"], f"Yay! I added the term '{message}'")
            self.sheet.insert([message])

    def post_message(self, channel, message):
        self.client.chat.post_message(
            channel=channel, text=message,
        )

    def upload(self, file, title, comment, channel):
        self.client.files.upload(
            file_=file, channels=[channel], title=title, initial_comment=comment
        )

    def run(self):
        rtm = self.client.rtm.start()
        url = rtm.body["url"]
        ws = websocket.WebSocket()
        ws.connect(url)
        while True:
            message = ws.recv()
            self.handle(message)

