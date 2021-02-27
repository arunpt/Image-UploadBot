import os
# Use @BotFather ~ @TeleORG_Bot

class Credentials:
	BOT_TOKEN = os.environ.get("BOT_TOKEN")
	API_ID = int(os.environ.get("API_ID"))
	API_HASH = os.environ.get("API_HASH")
	HOME_MSG = os.environ.get("HOME_MSG")
	ABOUT_MSG = os.environ.get("ABOUT_MSG")
	UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL")
	MONGODB_URI = os.environ.get("MONGODB_URI")
	SESSION_NAME = os.environ.get("SESSION_NAME")    
	ADMIN = os.environ.get("ADMIN")
