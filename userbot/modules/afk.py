# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """
import asyncio
from datetime import datetime
from random import randint

from telethon.events import StopPropagation

from userbot.events import register

from userbot import (  # noqa pylint: disable=unused-import isort:skip
    AFKREASON,
    COUNT_MSG,
    CMD_HELP,
    ISAFK,
    BOTLOG,
    BOTLOG_CHATID,
    USERS,
    PM_AUTO_BAN,
)


@register(incoming=True, disable_edited=True)
async def mention_afk(mention):
    """ This function takes care of notifying the people who mention you that you are AFK."""
    global COUNT_MSG
    global USERS
    global ISAFK
    global afk_time
    global afk_start
    global afk_end
    not_afk = datetime.now()
    afk_end = not_afk.replace(microsecond=0)
    if ISAFK and mention.message.mentioned:
        now = datetime.now()
        afk_since = now - afk_time
        day = float(afk_since.seconds) // (24 * 3600)
        time = float(afk_since.seconds) % (24 * 3600)
        hours = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        if day == 1:
            afk_str = "Yesterday"
        elif day > 1:
            if day > 6:
                date = now + datetime.timedelta(
                    days=-day, hours=-hours, minutes=-minutes
                )
                afk_str = date.strftime("%A, %Y %B %m, %H:%I")
            else:
                wday = now + datetime.timedelta(days=-day)
                afk_str = wday.strftime("%A")
        elif hours > 1:
            afk_str = f"`{int(hours)}h{int(minutes)}m` ago"
        elif minutes > 0:
            afk_str = f"`{int(minutes)}m{int(seconds)}s` ago"
        else:
            afk_str = f"`{int(seconds)}s` ago"

        is_bot = False
        if (sender := await mention.get_sender()) :
            is_bot = sender.bot
            if is_bot:
                return  # ignore bot

        chat_obj = await mention.client.get_entity(mention.chat_id)
        chat_title = chat_obj.title

        if mention.sender_id not in USERS or chat_title not in USERS:
            if AFKREASON:
                await mention.reply(
                    f"**I'm not available right now.** (Since: {afk_str})"
                    f"\nReason: `{AFKREASON}`."
                )
            else:
                await mention.reply(
                    f"**I'm not available right now.** (Since: {afk_str})"
                    "\n**Please come back later.**"
                )
            if mention.sender_id is not None:
                USERS.update({mention.sender_id: 1})
            else:
                USERS.update({chat_title: 1})
        else:
            if USERS[mention.sender_id] % randint(2, 4) == 0:
                if AFKREASON:
                    await mention.reply(
                        f"**I'm not available right now.** (Since: {afk_str})"
                        f"\nReason: `{AFKREASON}`."
                    )
                else:
                    await mention.reply(
                        f"**I'm not available right now.** (Since: {afk_str})"
                        "\n**Please come back later.**"
                    )
            if mention.sender_id is not None:
                USERS[mention.sender_id] += 1
            else:
                USERS[chat_title] += 1
        COUNT_MSG += 1


@register(incoming=True, disable_errors=True)
async def afk_on_pm(sender):
    """ Function which informs people that you are AFK in PM """
    global ISAFK
    global USERS
    global COUNT_MSG
    global afk_time
    global afk_start
    global afk_end
    not_afk = datetime.now()
    afk_end = not_afk.replace(microsecond=0)
    afk_str = "a while ago"
    if (
        sender.is_private
        and sender.sender_id != 777000
        and not (await sender.get_sender()).bot
    ):
        if PM_AUTO_BAN:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved

                apprv = is_approved(sender.sender_id)
            except AttributeError:
                apprv = True
        else:
            apprv = True
        if apprv and ISAFK:
            now = datetime.now()
            afk_since = now - afk_time
            day = float(afk_since.seconds) // (24 * 3600)
            time = float(afk_since.seconds) % (24 * 3600)
            hours = time // 3600
            time %= 3600
            minutes = time // 60
            time %= 60
            seconds = time
            if day == 1:
                afk_str = "Yesterday"
            elif day > 1:
                if day > 6:
                    date = now + datetime.timedelta(
                        days=-day, hours=-hours, minutes=-minutes
                    )
                    afk_since = date.strftime("%A, %Y %B %m, %H:%I")
                else:
                    wday = now + datetime.timedelta(days=-day)
                    afk_str = wday.strftime("%A")
            elif hours > 1:
                afk_str = f"`{int(hours)}h{int(minutes)}m` ago"
            elif minutes > 0:
                afk_str = f"`{int(minutes)}m{int(seconds)}s` ago"
            else:
                afk_str = f"`{int(seconds)}s` ago"
            if sender.sender_id not in USERS:
                if AFKREASON:
                    await sender.reply(
                        f"**I'm not available right now.** (Since: {afk_str})"
                        f"\nReason: `{AFKREASON}`."
                    )
                else:
                    await sender.reply(
                        f"**I'm not available right now.** (Since: {afk_str})"
                        "\n**Please come back later.**"
                    )
                USERS.update({sender.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif apprv and sender.sender_id in USERS:
                if USERS[sender.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await sender.reply(
                            "**I'm not available right now.** (Since: {afk_str})"
                            f"\nReason: `{AFKREASON}`."
                        )
                    else:
                        await sender.reply(
                            "**I'm not available right now.** (Since: {afk_str})"
                            "\n**Please come back later.**"
                        )
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern=r"^\.off(?: |$)(.*)", disable_errors=True)
async def set_afk(afk_e):
    """ For .afk command, allows you to inform people that you are afk when they message you """
    afk_e.text
    string = afk_e.pattern_match.group(1)
    global ISAFK
    global AFKREASON
    global afk_time
    global afk_start
    global afk_end
    afk_time = None
    afk_end = {}
    start1 = datetime.now()
    afk_start = start1.replace(microsecond=0)
    if string:
        AFKREASON = string
        await afk_e.edit("**Into The Void!**" f"\nReason: `{string}`")
    else:
        await afk_e.edit("**Into The Void!**")
    if BOTLOG:
        await afk_e.client.send_message(BOTLOG_CHATID, "#AFK\nYou went AFK!")
    ISAFK = True
    afk_time = datetime.now()
    raise StopPropagation


@register(outgoing=True, pattern=r"^\.unoff(?: |$)(.*)", disable_errors=True)
async def type_afk_is_not_true(notafk):
    """ This sets your status as not afk automatically when you write something while being afk """
    global ISAFK
    global COUNT_MSG
    global USERS
    global AFKREASON
    global afk_time
    global afk_start
    global afk_end
    not_afk = datetime.now()
    afk_end = not_afk.replace(microsecond=0)
    if ISAFK:
        ISAFK = False
        msg = await notafk.edit("**I'm back BISH!**")
        await asyncio.sleep(3)
        await msg.delete()
        if BOTLOG:
            await notafk.client.send_message(
                BOTLOG_CHATID,
                "You've received "
                + str(COUNT_MSG)
                + " messages from "
                + str(len(USERS))
                + " chats while you were away",
            )
            for i in USERS:
                if str(i).isnumeric():
                    name = await notafk.client.get_entity(i)
                    name0 = str(name.first_name)
                    await notafk.client.send_message(
                        BOTLOG_CHATID,
                        "["
                        + name0
                        + "](tg://user?id="
                        + str(i)
                        + ")"
                        + " sent you "
                        + "`"
                        + str(USERS[i])
                        + " message(s)`",
                    )
                else:  # anon admin
                    await notafk.client.send_message(
                        BOTLOG_CHATID,
                        "Anonymous admin in `"
                        + i
                        + "` sent you "
                        + "`"
                        + str(USERS[i])
                        + " message(s)`",
                    )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = None


CMD_HELP.update(
    {
        "afk": ">`.out [Optional Reason]`"
        "\nUsage: Sets you as afk.\nReplies to anyone who tags/PM's "
        "you telling them that you are AFK(reason)."
        "\n\n>`.in`"
        "\nUsage: Switches you off from AFK mode"
    }
)
