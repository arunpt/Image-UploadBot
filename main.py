# (c) CW4RR10R | @AbirHasan2005

import os
import uuid
import shutil
import logging
from pyrogram import Client, filters
from creds import Credentials
from telegraph import upload_file
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)


TGraph = Client(
    "Image upload bot",
    bot_token=Credentials.BOT_TOKEN,
    api_id=Credentials.API_ID,
    api_hash=Credentials.API_HASH,
)

home_text = """
Hi, [{}](tg://user?id={})
I am Telegram to telegra.ph image uploader bot.

Send me any Image I will upload to telegra.ph and give you link.
"""
about_text = """
🤖 **My Name:** [Telegraph Image Bot](https://t.me/AH_TelegraphBot)

📝 **Language:** [Python 3](https://www.python.org)

📚 **Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram)

📡 **Hosted on:** [Heroku](https://www.heroku.com)

👨‍💻 **Developer:** @AbirHasan2005

👥 **Support Group:** [Linux Repositories](https://t.me/linux_repo)

📢 **Updates Channel:** [Discovery Projects](https://t.me/Discovery_Updates)
"""

@TGraph.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"Hi, {message.from_user.mention}.\nI am Telegram to telegra.ph image uploader bot.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Updates Channel", url="https://t.me/Discovery_Updates"),
                    InlineKeyboardButton(text="Support Group", url="https://t.me/linux_repo")
                ],
                [
                    InlineKeyboardButton("About", callback_data="about")
                ]
            ]
        ),
        parse_mode="html",
        disable_web_page_preview=True
    )


@TGraph.on_message(filters.photo)
async def getimage(client, message):
    tmp = os.path.join("downloads", str(message.chat.id))
    if not os.path.isdir(tmp):
        os.makedirs(tmp)
    img_path = os.path.join(tmp, str(uuid.uuid4()) + ".jpg")
    dwn = await message.reply_text("Downloading ...", True)
    img_path = await client.download_media(message=message, file_name=img_path)
    await dwn.edit_text("Uploading ...")
    try:
        response = upload_file(img_path)
    except Exception as error:
        await dwn.edit_text(f"Oops, Something went wrong!\n\n{error}")
        return
    await dwn.edit_text(f"https://telegra.ph{response[0]}")
    shutil.rmtree(tmp, ignore_errors=True)

## The Callback Thing
#############################################
def dynamic_data_filter(data):
    async def func(flt, _, query):
        return flt.data == query.data

    return filters.create(func, data=data)
#############################################

@bot.on_callback_query(dynamic_data_filter("about"))
async def about_meh(_, query):
    buttons = [
        [
            InlineKeyboardButton("Go To Home", callback_data="home"),
            InlineKeyboardButton("Close", callback_data="closeit")
        ]
    ]
    await query.message.edit(
        about_text,
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    await query.answer()

@TGraph.on_callback_query(dynamic_data_filter("home"))
async def go_to_home(_, query):
    buttons = [
        [
            InlineKeyboardButton("Support Group", url="http://t.me/linux_repo"),
            InlineKeyboardButton("Updates Channel", url="http://t.me/Discovery_Updates")
        ],
        [
            InlineKeyboardButton("About", callback_data="about")
        ]
    ]
    await query.message.edit(
        home_text.format(query.message.chat.first_name, query.message.chat.id),
        parse_mode="markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

@TGraph.on_callback_query(dynamic_data_filter("closeit"))
def closebruh(_, query):
    query.message.delete()
    query.answer()
##

TGraph.run()
