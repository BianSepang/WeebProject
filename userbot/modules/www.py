# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to the \
    Information Superhighway (yes, Internet). """

from datetime import datetime

from speedtest import Speedtest
from telethon import functions

from userbot import CMD_HELP
from userbot.events import register
from userbot.utils import humanbytes


@register(outgoing=True, pattern=r"^\.speedtest$")
async def speedtst(spd):
    """ For .speed command, use SpeedTest to check server speeds. """
    await spd.edit("`Running speed test...`")

    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    msg = (
        f"**Started at {result['timestamp']}**\n\n"
        "**Client**\n"
        f"**ISP :** `{result['client']['isp']}`\n"
        f"**Country :** `{result['client']['country']}`\n\n"
        "**Server**\n"
        f"**Name :** `{result['server']['name']}`\n"
        f"**Country :** `{result['server']['country']}`\n"
        f"**Sponsor :** `{result['server']['sponsor']}`\n\n"
        f"**Ping :** `{result['ping']}`\n"
        f"**Upload :** `{humanbytes(result['upload'])}/s`\n"
        f"**Download :** `{humanbytes(result['download'])}/s`"
    )

    await spd.delete()
    await spd.client.send_file(
        spd.chat_id,
        result["share"],
        caption=msg,
        force_document=False,
    )


@register(outgoing=True, pattern=r"^\.dc$")
async def neardc(event):
    """ For .dc command, get the nearest datacenter information. """
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(
        f"Country : `{result.country}`\n"
        f"Nearest Datacenter : `{result.nearest_dc}`\n"
        f"This Datacenter : `{result.this_dc}`"
    )


@register(outgoing=True, pattern=r"^\.ping$")
async def pingme(pong):
    """ For .ping command, ping the userbot from any chat.  """
    start = datetime.now()
    await pong.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit("`Pong!\n%sms`" % (duration))


CMD_HELP.update(
    {
        "speedtest": ">`.speedtest`" "\nUsage: Does a speedtest and shows the results.",
        "dc": ">`.dc`" "\nUsage: Finds the nearest datacenter from your server.",
        "ping": ">`.ping`" "\nUsage: Shows how long it takes to ping your bot.",
    }
)
