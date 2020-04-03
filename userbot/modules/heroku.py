# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   Heroku manager for your userbot
"""

import heroku3
import asyncio
import requests
import math

from userbot import CMD_HELP, HEROKU_APP_NAME, HEROKU_API_KEY
from userbot.events import register

Heroku = heroku3.from_key(HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
             'AppleWebKit/537.36 (KHTML, like Gecko) '
             'Chrome/80.0.3987.149 Mobile Safari/537.36'
             )


@register(outgoing=True, pattern="^.dyno (restart|shutdown|usage)(?: |$)")
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = Heroku.app(HEROKU_APP_NAME)
    try:
        """ - Catch error if dyno not on - """
        Dyno = app.dynos()[0]
    except IndexError:
        app.scale_formation_process("worker", 1)
        return await dyno.edit(
            f"`Starting` ⬢**{HEROKU_APP_NAME}**`...`")
    dyno_name = Dyno.name
    exe = dyno.pattern_match.group(1)
    if exe == "restart":
        wait = 0.03
        dot = "."
        i = 0
        text = f"`Restarting` ⬢**{HEROKU_APP_NAME}**"
        await dyno.edit(text)
        Dyno.restart()
        up = False
        await asyncio.sleep(wait)
        while not up:
            loading_dot = text + dot
            await dyno.edit(loading_dot)
            i = i + 1
            await asyncio.sleep(wait)
            if i == 3:
                loading_dot = None
                i = 0
            state = Dyno.state
            if state == "up":
                up = True
                if i == 0:
                    await asyncio.sleep(0.05)
                    loading_dot = text + dot
                    await dyno.edit(loading_dot)
                    await asyncio.sleep(0.05)
                    loading_dot = loading_dot + dot
                    await dyno.edit(loading_dot)
                    await asyncio.sleep(0.05)
                    await dyno.edit(loading_dot + dot)
                if i == 1:
                    await asyncio.sleep(0.05)
                    loading_dot = loading_dot + dot
                    await dyno.edit(loading_dot)
                    await asyncio.sleep(0.05)
                    await dyno.edit(loading_dot + dot)
                elif i == 2:
                    await asyncio.sleep(0.05)
                    await dyno.edit(loading_dot + dot)
        return await dyno.edit(
            f"`Restarting` ⬢**{HEROKU_APP_NAME}**`... done`")
    elif exe == "shutdown":
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.heroku+json; version=3',
        }
        path = ("/apps/" + HEROKU_APP_NAME + "/dynos/" +
                dyno_name + "/actions/stop")
        r = requests.post(heroku_api + path, headers=headers)
        if r.status_code != 202:
            return await dyno.edit("`Error: something bad happened`\n\n"
                                   f">.`{r.reason}`\n")
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        await dyno.edit(f"`Shutdown` ⬢**{HEROKU_APP_NAME}**`... done`")
    elif exe == "usage":
        """ - Get your account Dyno Usage - """
        await dyno.edit("`Getting information...`")
        Apps = Heroku.apps()
        user_id = Heroku.account().id
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
        }
        path = "/accounts/" + user_id + "/actions/get-quota"
        r = requests.get(heroku_api + path, headers=headers)
        if r.status_code != 200:
            return await dyno.edit("`Error: something bad happened`\n\n"
                                   f">.`{r.reason}`\n")
        result = r.json()
        quota = result['account_quota']
        quota_used = result['quota_used']

        """ - Used - """
        remaining_quota = quota - quota_used
        percentage = math.floor(remaining_quota / quota * 100)
        minutes_remaining = remaining_quota / 60
        hours = math.floor(minutes_remaining / 60)
        minutes = math.floor(minutes_remaining % 60)

        """ - Current - """
        App = result['apps']
        try:
            App[0]['quota_used']
            App[1]['quota_used']
        except IndexError:
            App0QuotaUsed = 0
            App0Percentage = 0
            App1QuotaUsed = 0
            App1Percentage = 0
        else:
            App0QuotaUsed = App[0]['quota_used'] / 60
            App0Percentage = math.floor(App[0]['quota_used'] * 100 / quota)
            App1QuotaUsed = App[1]['quota_used'] / 60
            App1Percentage = math.floor(App[1]['quota_used'] * 100 / quota)
        App0Hours = math.floor(App0QuotaUsed / 60)
        App0Minutes = math.floor(App0QuotaUsed % 60)
        App1Hours = math.floor(App1QuotaUsed / 60)
        App1Minutes = math.floor(App1QuotaUsed % 60)

        await asyncio.sleep(1.5)

        return await dyno.edit(
            "**Dyno Usage**:\n\n"
            f" -> `Dyno usage for`  **{Apps[0].name}**:\n"
            f"     •  `{App0Hours}`**h**  `{App0Minutes}`**m**  "
            f"**|**  [`{App0Percentage}`**%**]"
            "\n"
            f" -> `Dyno usage for`  **{Apps[1].name}**:\n"
            f"     •  `{App1Hours}`**h**  `{App1Minutes}`**m**  "
            f"**|**  [`{App1Percentage}`**%**]"
            "\n\n"
            " -> `Dyno hours quota remaining this month`:\n"
            f"     •  `{hours}`**h**  `{minutes}`**m**  "
            f"**|**  [`{percentage}`**%**]"
        )


CMD_HELP.update({
    "dyno":
    ">.`dyno usage`"
    "\nUsage: Check your heroku dyno quota remainings and used quota app"
    "\n\n>.`dyno restart`"
    "\nUsage: Restart your dyno application, turned on it if not on"
    "\n\n>.`dyno shutdown`"
    "\nUsage: Shutdown completly"
})
