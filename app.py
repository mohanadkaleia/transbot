from flask import Flask
from slackeventsapi import SlackEventAdapter
import config


# This `app` represents your existing Flask app
app = Flask(__name__)


# An example of one of your Flask app's routes
@app.route("/")
def hello():
  return "Hello there!"


# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
slack_events_adapter = SlackEventAdapter(config.slack['secret'], "/slack/events", app)


# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on("message")
def reaction_added(event_data):  
  print('hello this is me')


# Start the server on port 3000
if __name__ == "__main__":
  app.run(port=3000)