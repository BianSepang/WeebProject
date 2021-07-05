# Copyright (C) 2021 dickymuliafiqri.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import requests
import io

from userbot import CMD_HELP
from userbot.events import register
from userbot.utils import chrome

@register(outgoing=True, pattern=r"^\.onecak")
async def onecak(event):
    await event.edit("`Processing...`")
    driver = await chrome()
    try:
        req = requests.get('https://onecak.azurewebsites.net/?shuffle')
        if req.status_code != 200:
            raise Exception(req.status_code)
        result = req.json()
        result = result['posts'][0]
        driver.get(result['url'])
        driver.get(result['src'])
        im_png = driver.find_element_by_xpath('/html/body/img').screenshot_as_png
        message_id = event.message.id
        if event.reply_to_msg_id:
            message_id = event.reply_to_msg_id
        with io.BytesIO(im_png) as out_file:
            out_file.name = "onecakdotcom.png"
            await event.edit("`Uploading onecak post as file..`")
            await event.client.send_file(
                event.chat_id,
                out_file,
                caption=f"[{result['title']}]({result['url']})",
                force_document=True,
                reply_to=message_id,
            )
    except Exception as err:
        await event.edit(f"Error {err}")


CMD_HELP.update(
    {
        "onecak": ">`.onecak`"
        "\nUsage: Get random post from 1cak.com.\n"
    }
)
