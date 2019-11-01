# Transbot 🤖
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/makes-people-smile.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

Transbot is a Python Slackbot that helps in translating AI terms from Arabic into English.

## Installation
This Slackbot is not intended to be installed anywhere, it is already installed on Slack workspace. I shared the source code of it if anyone wants to build something similar.
```bash
pip install -r requirments.txt
```

## Set the environment variables
In order to use the app, we need to set the following variables: 
```bash
export SLACK_BOT_TOKEN=xoxob**********
export GOOGLE_APPLICATION_CREDENTIALS="$(< cred.json)"
export SHEET_URL=https://google.sheet.url
```
Where the slack bot token is the token you get when setting up a Slack app. While you can get the cred.json when you set a Google cloud API project credentials. 

In case you deployed to Heruko, you need to set those variables there.

## Usage
```bash
pip install -r requirements
```

```python
python app.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
