# (c) CW4RR10R | @AbirHasan2005

import os
import uuid
import shutil
import logging
import asyncio
import traceback
from pyrogram import Client, filters
from core.creds import Credentials
from core.database import Database
from telegraph import upload_file
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

## --- Logger --- ##
logging.basicConfig(level=logging.INFO)


## --- Bot --- ##
TGraph = Client(
    Credentials.SESSION_NAME,
    bot_token=Credentials.BOT_TOKEN,
    api_id=Credentials.API_ID,
    api_hash=Credentials.API_HASH,
)


## --- Sub Configs --- ##
db = Database(Credentials.MONGODB_URI, Credentials.SESSION_NAME)
broadcast_ids = {}
home_text = None
if Credentials.HOME_MSG:
    home_text = Credentials.HOME_MSG
else:
    home_text = """
Hi, [{}](tg://user?id={})
I am Telegram to telegra.ph Image Uploader Bot.

Send me any Image I will upload to telegra.ph and give you link.
"""
about_text = None
if Credentials.ABOUT_MSG:
    about_text = Credentials.ABOUT_MSG
else:
    about_text = """
🤖 **My Name:** [Telegraph Image Bot](https://t.me/AH_TelegraphBot)

📝 **Language:** [Python 3](https://www.python.org)

📚 **Framework:** [Pyrogram](https://github.com/pyrogram/pyrogram) & [Telegraph](https://pypi.org/project/telegraph)

📡 **Hosted on:** [Heroku](https://heroku.com/deploy?template=https://github.com/Discovery-Projects/Image-UploadBot/tree/master)

👨‍💻 **Developer:** @AbirHasan2005

👥 **Support Group:** [Linux Repositories](https://t.me/linux_repo)

📢 **Updates Channel:** [Discovery Projects](https://t.me/Discovery_Updates)
"""
async def send_msg(user_id, message):
    try:
        await message.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


## --- Start Handler --- ##
@TGraph.on_message(filters.command("start"))
async def start(client, message):
    ## --- Users Adder --- ##
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
    ## --- Force Sub --- ##
    update_channel = Credentials.UPDATES_CHANNEL
    if update_channel:
        try:
            user = await client.get_chat_member(update_channel, message.from_user.id)
            if user.status == "kicked":
               await client.send_message(
                   chat_id=message.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/linux_repo).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/linux_repo).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return
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


@TGraph.on_message(filters.private & filters.command("status") & filters.user(Credentials.ADMIN))
async def sts(bot, cmd):
    total_users = await db.total_users_count()
    await cmd.reply_text(text=f"**Total Users in DB:** `{total_users}`", parse_mode="Markdown")


@TGraph.on_message(filters.private & filters.command("broadcast") & filters.user(Credentials.ADMIN) & filters.reply)
async def broadcast_(c, m):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
        text = f"Broadcast initiated! You will be notified with log file when all the users are notified."
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(
        total = total_users,
        current = done,
        failed = failed,
        success = success
    )
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(
                user_id = int(user['id']),
                message = broadcast_msg
            )
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(
                        current = done,
                        failed = failed,
                        success = success
                    )
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(
            text=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    else:
        await m.reply_document(
            document='broadcast.txt',
            caption=f"Broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
            quote=True
        )
    await aiofiles.os.remove('broadcast.txt')


@TGraph.on_message(filters.private & (filters.photo | filters.document))
async def getimage(client, message):
    ## --- Users Adder --- ##
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
    ## --- Force Sub --- ##
    update_channel = Credentials.UPDATES_CHANNEL
    if update_channel:
        try:
            user = await client.get_chat_member(update_channel, message.chat.id)
            if user.status == "kicked":
               await client.send_message(
                   chat_id=message.chat.id,
                   text="Sorry Sir, You are Banned!\nNow Your Can't Use Me. Contact my [Support Group](https://t.me/linux_repo).",
                   parse_mode="markdown",
                   disable_web_page_preview=True
               )
               return
        except UserNotParticipant:
            await client.send_message(
                chat_id=message.chat.id,
                text="**Please Join My Updates Channel to use this Bot!**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel", url=f"https://t.me/{update_channel}")
                        ]
                    ]
                ),
                parse_mode="markdown"
            )
            return
        except Exception:
            await client.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact my [Support Group](https://t.me/linux_repo).",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return
    if message.document:
        if not message.document.file_name.endswith(".jpg"):
            return
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
        await dwn.edit_text(f"Oops, Something went wrong!\n\n**Error:** {error}")
        return
    await dwn.edit_text(f"https://telegra.ph{response[0]}")
    shutil.rmtree(tmp, ignore_errors=True)

## --- Custom Callback Filter --- ##
def dynamic_data_filter(data):
    async def func(flt, _, query):
        return flt.data == query.data
    return filters.create(func, data=data)

@TGraph.on_callback_query(dynamic_data_filter("about"))
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
async def closeme(_, query):
    await query.message.delete()
    await query.answer()


TGraph.run()
