# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
"""
   fallback for main userbot
"""
import os
import asyncio
import requests
import math
import codecs
import shutil

from operator import itemgetter

from userbot import (
    heroku, fallback,
    HEROKU_APP_NAME, HEROKU_API_KEY, HEROKU_API_KEY_FALLBACK
)
from userbot.events import register


heroku_api = "https://api.heroku.com"
useragent = (
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/81.0.4044.117 Mobile Safari/537.36'
)

@register(outgoing=True, pattern=r"^\.dyno on(?: |$)(.*)")
async def dyno_manage(dyno):
    await dyno.edit("`Sending information...`")
    exe = dyno.pattern_match.group(1)
    if not exe:
        await dyno.edit(f"`Heroku App not found.\nPlease run` `'.dyno on <your app name>'`")
        return
    else:
        HEROKU_APP_NAME = exe
        app = heroku.app(HEROKU_APP_NAME)
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
            await dyno.delete()
            return True
        else:
            await dyno.edit(f"⬢**{HEROKU_APP_NAME}** `already on...`")
            return False


@register(outgoing=True,
           pattern=r"^\.dyno restart(?: |$)(.*)")
async def dyno_manage(dyno):
    await dyno.edit("`Sending information...`")
    exe = dyno.pattern_match.group(1)
    if not exe:
        await dyno.edit(f"`Heroku App not found.\nPlease run` `'.dyno restart <your app name>'`")
        return
    else:
        HEROKU_APP_NAME = exe
        app = heroku.app(HEROKU_APP_NAME)
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            """
               Tell user if main app dyno is not on
            """
            await dyno.respond(f"⬢**{HEROKU_APP_NAME}** `is not on...`")
            return False
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
            await dyno.delete()
            return True


@register(outgoing=True,
           pattern=r"^\.dyno off(?: |$)(.*)")
async def dyno_manage(dyno):
    await dyno.edit("`Sending information...`")
    exe = dyno.pattern_match.group(1)
    if not exe:
        await dyno.edit(f"`Heroku App not found.\nPlease run` `'.dyno off <your app name>'`")
        return
    else:
        HEROKU_APP_NAME = exe
        app = heroku.app(HEROKU_APP_NAME)
        """
           Complete shutdown
        """
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
        await dyno.delete()
        return True


@register(outgoing=True,
          pattern=(
              "^.dyno "
              "(usage|deploy|cancel deploy"
              "|cancel build|get log|help|update)(?: (.*)|$)")
          )
async def dyno_manage(dyno):
    await dyno.edit("`Sending information...`")
    exe = dyno.pattern_match.group(1)
    app = heroku.app(HEROKU_APP_NAME)
    if exe == "usage":
        """
           Get your account Dyno Usage
        """
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
                msg += f"`Cannot get {aydi} information...`\n\n"
                continue
            result = r.json()
            quota = result['account_quota']
            quota_used = result['quota_used']

            """
               Quota Limit Left and Used Quota
            """
            remaining_quota = quota - quota_used
            percentage = math.floor(remaining_quota / quota * 100)
            minutes_remaining = remaining_quota / 60
            hours = math.floor(minutes_remaining / 60)
            minutes = math.floor(minutes_remaining % 60)

            """
               Used Quota per/App
            """
            Apps = result['apps']
            """Sort from larger usage to lower usage"""
            Apps = sorted(Apps, key=itemgetter('quota_used'), reverse=True)
            if fallback is not None and fallback.account().id == aydi:
                apps = fallback.apps()
                msg += "**Dyno Usage fallback-account**:\n\n"
            else:
                apps = heroku.apps()
                msg += "**Dyno Usage main-account**:\n\n"
            if len(Apps) == 0:
                for App in apps:
                    msg += (
                        f" -> `Dyno usage for`  **{App.name}**:\n"
                        f"     •  `0`**h**  `0`**m**  "
                        f"**|**  [`0`**%**]\n\n"
                    )
            else:
                for App in Apps:
                    AppName = '__~~Deleted or transferred app~~__'
                    ID = App.get('app_uuid')

                    AppQuota = App.get('quota_used')
                    AppQuotaUsed = AppQuota / 60
                    AppPercentage = math.floor(AppQuota * 100 / quota)
                    AppHours = math.floor(AppQuotaUsed / 60)
                    AppMinutes = math.floor(AppQuotaUsed % 60)

                    for name in apps:
                        if ID == name.id:
                            AppName = f"**{name.name}**"
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
        await dyno.edit(msg)
        return
    if exe == "deploy":
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
            '`[HEROKU - MAIN]`\n'
            '`Userbot deploy in progress, please wait...`'
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
    elif exe == "cancel deploy" or exe == "cancel build":
        """
           Only cancel 1 recent builds from activity if build.id not supplied
        """
        build_id = dyno.pattern_match.group(2)
        if build_id is None:
            build = app.builds(order_by='created_at', sort='desc')[0]
        else:
            build = app.builds().get(build_id)
            if build is None:
                await dyno.edit(
                    f"`There is no such build.id`:\n**{build_id}**")
                return False
        if build.status != "pending":
            await dyno.edit("`Zero active builds to cancel...`")
            return False
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.cancel-build',
        }
        path = "/apps/" + build.app.id + "/builds/" + build.id
        r = requests.delete(heroku_api + path, headers=headers)
        text = f"`Stopping build`  ⬢**{build.app.name}**"
        await dyno.edit(text)
        sleep = 1
        dot = "."
        await asyncio.sleep(2)
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(
            "`[HEROKU]`\n"
            f"Build: ⬢**{build.app.name}**  `Stopped...`")
        await dyno.delete()
        return True
    elif exe == "get log":
        await dyno.edit("`Getting information...`")
        with open('logs.txt', 'w') as log:
            log.write(app.get_log())
        fd = codecs.open("logs.txt", "r", encoding="utf-8")
        data = fd.read()
        key = (requests.post("https://nekobin.com/api/documents",
                             json={"content": data}) .json() .get("result") .get("key"))
        url = f"https://nekobin.com/raw/{key}"
        await dyno.edit(f"`Here the heroku logs:`\n\nPasted to: [Nekobin]({url})")
        os.remove('logs.txt')
        return True
    elif exe == "help":
        await dyno.edit(
            ">`.dyno usage`"
            "\nUsage: Check your heroku App usage dyno quota."
            "\nIf one of your app usage is empty, it won't be write in output."
            "\n\n>`.dyno on <app name>`"
            "\nUsage: Turn on your your dyno application."
            "\n\n>`.dyno restart <app name>`"
            "\nUsage: Restart your dyno application."
            "\n\n>`.dyno off <app name>`"
            "\nUsage: Shutdown dyno completly."
            "\n\n>`.dyno cancel deploy` or >`.dyno cancel build`"
            "\nUsage: Cancel deploy from main app "
            "give build.id to specify build to cancel."
            "\n\n>`.dyno get log`"
            "\nUsage: Get your main dyno recent logs."
            "\n\n>`.dyno help`"
            "\nUsage: print this help."
        )
        return True
    elif exe == "update":
        await dyno.edit(
            ">`.updatef`"
            "\nUsage: Check fallback if there are any updates."
            "\n\n>`.updatef deploy`"
            "\nUsage: If there are any updates, you can deploy fallback app."
            "\n\n>`.updatef now`"
            "\nUsage: If there are any updates, you can update fallback app."
            "\n\n"
            "**FAQ**:\n"
            "`Q`: What's different >`.updatef now` and >`.updatef deploy`?\n"
            "`A`: >`.updatef now` update your fallback without deploying, "
            "but the app will back to latest successfully deployed state if "
            "fallback restarted.\n"
            ">`.updatef deploy` is more same but if fallback restarted it "
            "won't rollback."
        )
        return True
