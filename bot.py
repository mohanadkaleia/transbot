import os
import slack

class Bot:

    def __init__(self, name, token):
        self.token = token
        self.name = name

    def run(self):
        while True:            
            rtm_client = slack.RTMClient(token=self.token)
            rtm_client.start()

    @slack.RTMClient.run_on(event='message')
    def handle(self, event):
        print(event)




