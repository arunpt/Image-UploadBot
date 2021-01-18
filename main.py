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


@TGraph.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"Hi, {message.from_user.mention}.\nI am Telegram to telegra.ph image uploader bot.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Updates Channel", url="https://t.me/Discovery_Updates"),
                    InlineKeyboardButton(text="Support Group", url="https://t.me/linux_repo")
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


TGraph.run()
