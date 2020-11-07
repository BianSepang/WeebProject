# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module containing userid, chatid and log commands"""

from asyncio import sleep

from telethon import functions

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import register
from userbot.modules.admin import get_user_from_event


@register(outgoing=True, pattern=r"^\.userid$")
async def useridgetter(target):
    """ For .userid command, returns the ID of the target user. """
    message = await target.get_reply_message()
    if message:
        if not message.forward:
            user_id = message.sender.id
            if message.sender.username:
                name = "@" + message.sender.username
            else:
                name = "**" + message.sender.first_name + "**"
        else:
            user_id = message.forward.sender.id
            if message.forward.sender.username:
                name = "@" + message.forward.sender.username
            else:
                name = "*" + message.forward.sender.first_name + "*"
        await target.edit("**Name:** {} \n**User ID:** `{}`".format(name, user_id))


@register(outgoing=True, pattern=r"^\.link(?: |$)(.*)")
async def permalink(mention):
    """ For .link command, generates a link to the user's PM with a custom text. """
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if custom:
        await mention.edit(f"[{custom}](tg://user?id={user.id})")
    else:
        tag = (
            user.first_name.replace("\u2060", "") if user.first_name else user.username
        )
        await mention.edit(f"[{tag}](tg://user?id={user.id})")


@register(outgoing=True, pattern=r"^\.chatid$")
async def chatidgetter(chat):
    """ For .chatid, returns the ID of the chat you are in at that moment. """
    await chat.edit("Chat ID: `" + str(chat.chat_id) + "`")


@register(outgoing=True, pattern=r"^\.log(?: |$)([\s\S]*)")
async def log(log_text):
    """ For .log command, forwards a message or the command argument to the bot logs group """
    if BOTLOG:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif log_text.pattern_match.group(1):
            user = f"#LOG / Chat ID: {log_text.chat_id}\n\n"
            textx = user + log_text.pattern_match.group(1)
            await bot.send_message(BOTLOG_CHATID, textx)
        else:
            return await log_text.edit("`What am I supposed to log?`")
        await log_text.edit("`Logged Successfully`")
    else:
        await log_text.edit("`This feature requires Logging to be enabled!`")
    await sleep(2)
    await log_text.delete()


@register(outgoing=True, pattern=r"^\.invite(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    to_add_users = event.pattern_match.group(1)
    if event.is_private:
        await event.edit("`.invite` users to a chat, not to a Private Message")
    else:
        if not event.is_channel and event.is_group:
            # https://lonamiwebs.github.io/Telethon/methods/messages/add_chat_user.html
            for user_id in to_add_users.split(" "):
                try:
                    await event.client(
                        functions.messages.AddChatUserRequest(
                            chat_id=event.chat_id, user_id=user_id, fwd_limit=1000000
                        )
                    )
                except Exception as e:
                    await event.edit(str(e))
                    return
            await event.edit("`Invited Unsuccessfully`")
            await sleep(3)
            await event.delete()
        else:
            # https://lonamiwebs.github.io/Telethon/methods/channels/invite_to_channel.html
            for user_id in to_add_users.split(" "):
                try:
                    await event.client(
                        functions.channels.InviteToChannelRequest(
                            channel=event.chat_id, users=[user_id]
                        )
                    )
                except Exception as e:
                    await event.edit(str(e))
                    return
            await event.edit("`Invited Successfully`")
            await sleep(3)
            await event.delete()


@register(outgoing=True, pattern=r"^\.kickme$")
async def kickme(leave):
    """ Basically it's .kickme command """
    await leave.edit("Nope, no, no, I go away")
    await leave.client.kick_participant(leave.chat_id, "me")


@register(outgoing=True, pattern=r"^\.unmutechat$")
async def unmute_chat(unm_e):
    """ For .unmutechat command, unmute a muted chat. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import unkread
    except AttributeError:
        return await unm_e.edit("`Running on Non-SQL Mode!`")
    unkread(str(unm_e.chat_id))
    await unm_e.edit("```Unmuted this chat Successfully```")
    await sleep(2)
    await unm_e.delete()


@register(outgoing=True, pattern=r"^\.mutechat$")
async def mute_chat(mute_e):
    """ For .mutechat command, mute any chat. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import kread
    except AttributeError:
        return await mute_e.edit("`Running on Non-SQL mode!`")
    await mute_e.edit(str(mute_e.chat_id))
    kread(str(mute_e.chat_id))
    await mute_e.edit("`Shush! This chat will be silenced!`")
    await sleep(2)
    await mute_e.delete()
    if BOTLOG:
        await mute_e.client.send_message(
            BOTLOG_CHATID, str(mute_e.chat_id) + " was silenced."
        )


@register(incoming=True, disable_errors=True)
async def keep_read(message):
    """ The mute logic. """
    try:
        from userbot.modules.sql_helper.keep_read_sql import is_kread
    except AttributeError:
        return
    kread = is_kread()
    if kread:
        for i in kread:
            if i.groupid == str(message.chat_id):
                await message.client.send_read_acknowledge(message.chat_id)


# Regex-Ninja module by @Kandnub
regexNinja = False


@register(outgoing=True, pattern="^s/")
async def sedNinja(event):
    """For regex-ninja module, auto delete command starting with s/"""
    if regexNinja:
        await sleep(0.5)
        await event.delete()


@register(outgoing=True, pattern=r"^\.regexninja (on|off)$")
async def sedNinjaToggle(event):
    """ Enables or disables the regex ninja module. """
    global regexNinja
    if event.pattern_match.group(1) == "on":
        regexNinja = True
        await event.edit("`Successfully enabled ninja mode for Regexbot.`")
        await sleep(1)
        await event.delete()
    elif event.pattern_match.group(1) == "off":
        regexNinja = False
        await event.edit("`Successfully disabled ninja mode for Regexbot.`")
        await sleep(1)
        await event.delete()


@register(outgoing=True, pattern=r"^\.create (b|g|c)(?: |$)(.*)")
async def telegraphs(grop):
    """For .create command, Creating New Group & Channel"""
    if grop.text[0].isalpha() or grop.text[0] in ("/", "#", "@", "!"):
        return
    if grop.fwd_from:
        return
    type_of_group = grop.pattern_match.group(1)
    group_name = grop.pattern_match.group(2)
    if type_of_group == "b":
        try:
            result = await grop.client(
                functions.messages.CreateChatRequest(  # pylint:disable=E0602
                    users=["@RemmuChan_bot"],
                    # Not enough users (to create a chat, for example)
                    # Telegram, no longer allows creating a chat with ourselves
                    title=group_name,
                )
            )
            created_chat_id = result.chats[0].id
            result = await grop.client(
                functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                )
            )
            await grop.edit(
                "Your {0} Group Created Successfully. Click [{0}]({1}) to join".format(
                    group_name, result.link
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await grop.edit(str(e))
    elif type_of_group in ("g", "c"):
        try:
            r = await grop.client(
                functions.channels.CreateChannelRequest(  # pylint:disable=E0602
                    title=group_name,
                    about="Welcome to this Channel",
                    megagroup=not bool(type_of_group == "c"),
                )
            )
            created_chat_id = r.chats[0].id
            result = await grop.client(
                functions.messages.ExportChatInviteRequest(
                    peer=created_chat_id,
                )
            )
            await grop.edit(
                "Your {0} Group/Channel Created Successfully. Click [{0}]({1}) to join".format(
                    group_name, result.link
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await grop.edit(str(e))


CMD_HELP.update(
    {
        "create": "**Create**"
        "\nUsage: Create Channel, Group & Group With Bot."
        "\n\n>`.create g`"
        "\nUsage: Create a Private Group."
        "\n\n>`.create b`"
        "\nUsage: Create a Group with Bot."
        "\n\n>`.create c`"
        "\nUsage: Create a Channel."
    }
)


CMD_HELP.update(
    {
        "chat": ">`.chatid`"
        "\nUsage: Fetches the current chat's ID"
        "\n\n>`.userid`"
        "\nUsage: Fetches the ID of the user in reply, if its a forwarded message, finds the ID for the source."
        "\n\n>`.log`"
        "\nUsage: Forwards the message you've replied to in your bot logs group."
        "\n\n>`.kickme`"
        "\nUsage: Leave from a targeted group."
        "\n\n>`.invite` <username>"
        "\nUsage: Invite user or bots with username"
        "\n\n>`.unmutechat`"
        "\nUsage: Unmutes a muted chat."
        "\n\n>`.mutechat`"
        "\nUsage: Allows you to mute any chat."
        "\n\n>`.link <username/userid> : <optional text>` (or) reply to someone's message with"
        "\n\n>`.link <optional text>`"
        "\nUsage: Generate a permanent link to the user's profile with optional custom text."
        "\n\n>`.regexninja on/off`"
        "\nUsage: Globally enable/disables the regex ninja module."
        "\nRegex Ninja module helps to delete the regex bot's triggering messages."
    }
)
