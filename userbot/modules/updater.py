# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
# credits to @AvinashReddy3108
#
"""
This module updates the userbot based on upstream revision
"""

import asyncio
import sys
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import (
    CMD_HELP,
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    UPSTREAM_REPO_BRANCH,
    UPSTREAM_REPO_URL,
)
from userbot.events import register

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), "requirements.txt"
)


async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"•[{c.committed_datetime.strftime(d_form)}]: "
            f"{c.summary} <{c.author}>\n"
        )
    return ch_log


async def print_changelogs(event, ac_br, changelog):
    changelog_str = (
        f"**Pembaruan** baru tersedia untuk **[{ac_br}]**:\n\n**Perubahan:**\n`{changelog}`"
    )
    if len(changelog_str) > 4096:
        await event.edit("`Perubahan terlalu besar, lihat berkas untuk melihatnya.`")
        file = open("output.txt", "w+")
        file.write(changelog_str)
        file.close()
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
        )
        remove("output.txt")
    else:
        await event.client.send_message(
            event.chat_id,
            changelog_str,
            reply_to=event.id,
        )
    return True


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            " ".join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                "`Harap siapkan variabel HEROKU_APP_NAME"
                " untuk dapat menggunakan userbot Anda...`"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f"{txt}\n" "`Kredensial Heroku tidak valid untuk men-deploy dyno userbot.`"
            )
            return repo.__del__()
        await event.edit("`Dyno userbot dalam proses, tunggu sebentar...`")
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except Exception as error:
            await event.edit(f"{txt}\n`Ini log kesalahannya:\n{error}`")
            return repo.__del__()
        build = app.builds(order_by="created_at", sort="desc")[0]
        if build.status == "failed":
            await event.edit(
                "`Pembuatan gagal!\n" "Dibatalkan atau ada beberapa kesalahan...`"
            )
            await asyncio.sleep(5)
            return await event.delete()
        else:
            await event.edit("`Berhasil diterapkan!\n" "Memulai ulang, tunggu sebentar...`")
    else:
        await event.edit("`Harap siapkan variabel HEROKU_API_KEY...`")
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    await event.edit(
        "`Berhasil diperbarui!\n" "Mulai ulang Bot... tunggu sebentar!`"
    )
    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)
    return


@register(outgoing=True, pattern=r"^\.update( now| deploy|$)")
async def upstream(event):
    "For .update command, check if the bot is up to date, update if specified"
    await event.edit("`Mendapatkan informasi....`")
    conf = event.pattern_match.group(1).strip()
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "`Oops.. Pembaruan tidak bisa dilanjutkan "
        txt += "terjadi beberapa masalah`\n\n**JEJAK LOG:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n`direktori {error} tidak ditemukan`")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n`Kegagalan awal! {error}`")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"`Sayangnya, direktori {error} tersebut "
                "tampaknya bukan repositori git.\n"
                "Tapi kita bisa memperbaikinya dengan memperbarui "
                "paksa userbot menggunakan .update now.`"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            "**[PEMBARUAN]:**\n"
            f"`Sepertinya Anda menggunakan kustom branch ({ac_br}) Anda sendiri. "
            "dalam hal ini, Pembaruan tidak dapat mengidentifikasi "
            "branch mana yang akan digabungkan. "
            "silahkan periksa branch resmi`"
        )
        return repo.__del__()
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    """ - Special case for deploy - """
    if conf == "deploy":
        await event.edit("`Menerapkan userbot, tunggu sebentar....`")
        await deploy(event, repo, ups_rem, ac_br, txt)
        return

    if changelog == "" and force_update is False:
        await event.edit(
            f"\n`Userbot Anda sudah`  **terbaru**  `dengan`  "
            f"**{UPSTREAM_REPO_BRANCH}**\n"
        )
        return repo.__del__()

    if conf == "" and force_update is False:
        await print_changelogs(event, ac_br, changelog)
        await event.delete()
        return await event.respond('`ketik ".update now / .update deploy" untuk memperbarui.`')

    if force_update:
        await event.edit(
            "`Sinkronisasi paksa ke kode userbot stabil terbaru, tunggu sebentar...`"
        )
    if conf == "now":
        await event.edit("`Memperbarui userbot, tunggu sebentar...`")
        await update(event, repo, ups_rem, ac_br)
    return


CMD_HELP.update(
    {
        "update": ">`.update`"
        "\nUntuk: Memeriksa apakah repositori userbot utama memiliki pembaruan "
        "dan juga menampilkan perubahan jika ada."
        "\n\n>`.update now`"
        "\nUntuk: Perbarui userbot Anda, "
        "jika ada pembaruan di repositori userbot Anda."
        "\n\n>`.update deploy`"
        "\nUntuk: Terapkan userbot Anda."
        "\nIni akan selalu memicu penerapan, bahkan jika tidak ada pembaruan."
    }
)
