# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
""" - a fallback for main userbot - """
import os
import asyncio
import requests
import math
import shutil

from operator import itemgetter
from git import Repo
from git.exc import GitCommandError

from userbot import (
    heroku, fallback,
    HEROKU_APP_NAME, HEROKU_API_KEY, HEROKU_API_KEY_FALLBACK,
    UPSTREAM_REPO_URL, MAIN_REPO_BRANCH
)
from userbot.events import register


heroku_api = "https://api.heroku.com"
useragent = (
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/81.0.4044.117 Mobile Safari/537.36'
)


@register(outgoing=True,
          pattern=(
              "^.dyno "
              "(on|restart|off|usage|deploy|get log|help)"
              "(?: |$)")
          )
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = heroku.app(HEROKU_APP_NAME)
    exe = dyno.pattern_match.group(1)
    if exe == "on":
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            app.scale_formation_process("worker", 1)
            text = f"`Starting` ⬢**{HEROKU_APP_NAME}**"
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `up...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
        else:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `already on...`")
    if exe == "restart":
        try:
            """ - Catch error if dyno not on - """
            Dyno = app.dynos()[0]
        except IndexError:
            return await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `is not on...`")
        else:
            text = f"`Restarting` ⬢**{HEROKU_APP_NAME}**"
            Dyno.restart()
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `restarted...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `crashed...`")
            return await dyno.delete()
    elif exe == "off":
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        text = f"`Shutdown` ⬢**{HEROKU_APP_NAME}**"
        sleep = 1
        dot = "."
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `turned off...`")
        return await dyno.delete()
    elif exe == "usage":
        """ - Get your account Dyno Usage - """
        await dyno.edit("`Getting information...`")
        headers = {
            'User-Agent': useragent,
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
        }
        user_id = []
        user_id.append(heroku.account().id)
        if fallback is not None:
            user_id.append(fallback.account().id)
        msg = ''
        for aydi in user_id:
            if fallback is not None and fallback.account().id == aydi:
                headers['Authorization'] = f'Bearer {HEROKU_API_KEY_FALLBACK}'
            else:
                headers['Authorization'] = f'Bearer {HEROKU_API_KEY}'
            path = "/accounts/" + aydi + "/actions/get-quota"
            r = requests.get(heroku_api + path, headers=headers)
            if r.status_code != 200:
                await dyno.edit("`Cannot get information...`")
                continue
            result = r.json()
            quota = result['account_quota']
            quota_used = result['quota_used']

            """ - Used - """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)

            """ - Used per/App Usage - """
            Apps = result['apps']
            """ - Sort from larger usage to lower usage - """
            Apps = sorted(Apps, key=itemgetter('quota_used'), reverse=True)
            if fallback is not None and fallback.account().id == aydi:
                apps = fallback.apps()
                msg += f"**Dyno Usage {fallback.account().email}**:\n\n"
            else:
                apps = heroku.apps()
                msg += f"**Dyno Usage {heroku.account().email}**:\n\n"
            try:
                Apps[0]
            except IndexError:
                """ - If all apps usage are zero - """
                for App in apps:
                    msg += (
                        f" -> `Dyno usage for`  **{App.name}**:\n"
                        f"     •  `0`**h**  `0`**m**  "
                        f"**|**  [`0`**%**]\n\n"
                    )
            for App in Apps:
                AppName = '__~~Deleted or transferred app~~__'
                ID = App.get('app_uuid')
                try:
                    AppQuota = App.get('quota_used')
                    AppQuotaUsed = AppQuota / 60
                    AppPercentage = math.floor(AppQuota * 100 / quota)
                except IndexError:
                    AppQuotaUsed = 0
                    AppPercentage = 0
                finally:
                    AppHours = math.floor(AppQuotaUsed / 60)
                    AppMinutes = math.floor(AppQuotaUsed % 60)
                    for names in apps:
                        if ID == names.id:
                            AppName = f"**{names.name}**"
                            break
                    msg += (
                        f" -> `Dyno usage for`  {AppName}:\n"
                        f"     •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
                        f"**|**  [`{AppPercentage}`**%**]\n\n"
                    )
            msg = (
                f"{msg}"
                " -> `Dyno hours quota remaining this month`:\n"
                f"     •  `{hours}`**h**  `{minutes}`**m**  "
                f"**|**  [`{percentage}`**%**]\n\n"
            )
        if msg:
            return await dyno.edit(msg)
        else:
            return
    elif exe == "deploy":
        home = os.getcwd()
        if not os.path.isdir('deploy'):
            os.mkdir('deploy')
        txt = (
            "`Oops.. cannot continue deploy due to "
            "some problems occured.`\n\n**LOGTRACE:**\n"
        )
        heroku_app = None
        apps = heroku.apps()
        for app in apps:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await dyno.edit(
                f"{txt}\n"
                "`Invalid Heroku credentials for deploying userbot dyno.`"
            )
            return
        await dyno.edit(
            '`[HEROKU - MAIN]`:\n'
            '`Userbot main dyno build in progress, please wait...`'
        )
        os.chdir('deploy')
        repo = Repo.init()
        origin = repo.create_remote('deploy', UPSTREAM_REPO_URL)
        try:
            origin.pull(MAIN_REPO_BRANCH)
        except GitCommandError:
            await dyno.edit(
                f"{txt}\n"
                f"`Invalid`  **{MAIN_REPO_BRANCH}** `branch name.`"
            )
            os.remove('deploy')
            return
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@")
        remote = repo.create_remote("heroku", heroku_git_url)
        remote.push(refspec="HEAD:refs/heads/master", force=True)
        await dyno.edit('`Successfully deployed!\n'
                        'Restarting, please wait...`')
        os.chdir(home)
        shutil.rmtree('deploy')
        return
    elif exe == "get log":
        await dyno.edit("`Getting information...`")
        with open('logs.txt', 'w') as log:
            log.write(app.get_log())
        await dyno.client.send_file(
            dyno.chat_id,
            "logs.txt",
            reply_to=dyno.id,
            caption="`Main dyno logs...`",
        )
        await dyno.edit("`Information gets and sent back...`")
        await asyncio.sleep(5)
        await dyno.delete()
        return os.remove('logs.txt')
    elif exe == "help":
        return await dyno.edit(
            ">`.dyno usage`"
            "\nUsage: Check your heroku App usage dyno quota."
            "\nIf one of your app usage is empty, it won't be write in output."
            "\n\n>`.dyno on`"
            "\nUsage: Turn on your main dyno application."
            "\n\n>`.dyno restart`"
            "\nUsage: Restart your dyno application."
            "\n\n>`.dyno off`"
            "\nUsage: Shutdown dyno completly."
            "\n\n>`.dyno deploy`"
            "\nUsage: Deploy your main userbot without checking update."
            "\n\n>`.dyno get log`"
            "\nUsage: Get your main dyno recent logs."
            "\n\n>`.dyno help`"
            "\nUsage: print this help."
        )
