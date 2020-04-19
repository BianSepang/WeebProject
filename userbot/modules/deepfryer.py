import os
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from userbot.events import register
from userbot import TEMP_DOWNLOAD_DIRECTORY


@register(outgoing=True, pattern='^.df(:? |$)')
async def _(fry):
    await fry.edit("`Sending information...`")
    if fry.fwd_from:
        return
    if not fry.reply_to_msg_id:
        await fry.edit("`Reply to any user message photo...`")
        return
    reply_message = await fry.get_reply_message()
    if not reply_message.media:
        await fry.edit("`No image found to fry...`")
        return
    if reply_message.sender.bot:
        await fry.edit("`Reply to actual user...`")
        return
    chat = "@image_deepfrybot"
    message_id_to_reply = fry.message.reply_to_msg_id
    async with fry.client.conversation(chat) as conv:
        try:
            response = conv.wait_event(events.NewMessage(incoming=True,
                                       from_users=432858024))
            await fry.client.send_message(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await fry.reply("Please unblock` @image_deepfrybot`...`")
            return
        if response.text.startswith("Forward"):
            await fry.edit("`Please disable your forward privacy setting...`")
        else:
            downloaded_file_name = await fry.client.download_media(
                                 response.message.media,
                                 TEMP_DOWNLOAD_DIRECTORY
            )
            await fry.client.send_file(
                fry.chat_id,
                downloaded_file_name,
                force_document=False,
                reply_to=message_id_to_reply
            )
            return os.remove(downloaded_file_name)
