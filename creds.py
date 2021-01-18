import os
#from dotenv import load_dotenv, find_dotenv

#load_dotenv(find_dotenv())


class Credentials:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")  # from @botfather
    API_ID = int(os.environ.get("API_ID"))  # from https://my.telegram.org/apps
    API_HASH = os.environ.get("API_HASH")  # from https://my.telegram.org/apps

# Okay 🤣
