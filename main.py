from pyrogram import Client
from creds import my
plugins = dict(
        root="plugins"
    )
bot = Client(
    "Image upload bot",
    bot_token = my.BOT_TOKEN,
    api_id = my.API_ID,
    api_hash = my.API_HASH,
    plugins = plugins
)
bot.run()