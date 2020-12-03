# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about the server. """

from asyncio import create_subprocess_exec as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from os import remove
from platform import python_version, uname
from shutil import which

from git import Repo
from telethon import version
from telethon.errors.rpcerrorlist import MediaEmptyError

from userbot import ALIVE_LOGO, ALIVE_NAME, CMD_HELP, bot
from userbot.events import register

# ================= CONSTANT =================
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
repo = Repo()
# ============================================


@register(outgoing=True, pattern=r"^\.sysd$")
async def sysdetails(sysd):
    """ For .sysd command, get system info using neofetch. """
    if not sysd.text[0].isalpha() and sysd.text[0] not in ("/", "#", "@", "!"):
        try:
            fetch = await asyncrunapp(
                "neofetch",
                "--stdout",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await fetch.communicate()
            result = str(stdout.decode().strip()) + str(stderr.decode().strip())

            await sysd.edit("`" + result + "`")
        except FileNotFoundError:
            await sysd.edit("`Instal neofetch terlebih dahulu!`")


@register(outgoing=True, pattern=r"^\.botver$")
async def bot_ver(event):
    """ For .botver command, get the bot version. """
    if not event.text[0].isalpha() and event.text[0] not in ("/", "#", "@", "!"):
        if which("git") is not None:
            ver = await asyncrunapp(
                "git",
                "describe",
                "--all",
                "--long",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )
            stdout, stderr = await ver.communicate()
            verout = str(stdout.decode().strip()) + str(stderr.decode().strip())

            rev = await asyncrunapp(
                "git",
                "rev-list",
                "--all",
                "--count",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )
            stdout, stderr = await rev.communicate()
            revout = str(stdout.decode().strip()) + str(stderr.decode().strip())

            await event.edit(
                "`Versi Userbot: " f"{verout}" "` \n" "`Revisi: " f"{revout}" "`"
            )
        else:
            await event.edit(
                "Sayang sekali Anda tidak memiliki git, Anda tetap menjalankan 'v1.beta.4'!"
            )


@register(outgoing=True, pattern=r"^\.pip(?: |$)(.*)")
async def pipcheck(pip):
    """ For .pip command, do a pip search. """
    if not pip.text[0].isalpha() and pip.text[0] not in ("/", "#", "@", "!"):
        pipmodule = pip.pattern_match.group(1)
        if pipmodule:
            await pip.edit("`Mencari...`")
            pipc = await asyncrunapp(
                "pip3",
                "search",
                pipmodule,
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await pipc.communicate()
            pipout = str(stdout.decode().strip()) + str(stderr.decode().strip())

            if pipout:
                if len(pipout) > 4096:
                    await pip.edit("`Output terlalu besar, dikirim sebagai file`")
                    file = open("output.txt", "w+")
                    file.write(pipout)
                    file.close()
                    await pip.client.send_file(
                        pip.chat_id,
                        "output.txt",
                        reply_to=pip.id,
                    )
                    remove("output.txt")
                    return
                await pip.edit(
                    "**Kueri: **\n`"
                    f"pip3 search {pipmodule}"
                    "`\n**Hasil: **\n`"
                    f"{pipout}"
                    "`"
                )
            else:
                await pip.edit(
                    "**Kueri: **\n`"
                    f"pip3 search {pipmodule}"
                    "`\n**Hasil: **\n`Tidak ada hasil yang dikembalikan/salah`"
                )
        else:
            await pip.edit("`Gunakan .help pip untuk melihat contoh`")


@register(outgoing=True, pattern=r"^\.(alive|on)$")
async def amireallyalive(alive):
    """For .alive command, check if the bot is running."""
    logo = ALIVE_LOGO
    output = (
        f"`WeebProject aktif, siap melayani Anda`\n"
        f"`=====================================`\n"
        f"`• Python         :   v{python_version()}`\n"
        f"`• Telethon       :   v{version.__version__}`\n"
        f"`• Pengguna       :   {DEFAULTUSER}`\n"
        f"`=====================================`\n"
        f"`======== berjalan di {repo.active_branch.name} =========`\n"
    )
    if ALIVE_LOGO:
        try:
            logo = ALIVE_LOGO
            await bot.send_file(alive.chat_id, logo, caption=output)
            await alive.delete()
        except MediaEmptyError:
            await alive.edit(
                output + "\n\n`Logo yang diberikan tidak valid."
                "\nPastikan link diarahkan ke gambar logo`."
            )
    else:
        await alive.edit(output)


@register(outgoing=True, pattern=r"^\.aliveu")
async def amireallyaliveuser(username):
    """ For .aliveu command, change the username in the .alive command. """
    message = username.text
    output = ".aliveu [pengguna baru tanpa tanda kurung] juga tidak bisa kosong"
    if not (message == ".aliveu" or message[7:8] != " "):
        newuser = message[8:]
        global DEFAULTUSER
        DEFAULTUSER = newuser
        output = "Berhasil mengubah pengguna menjadi " + newuser + "!"
    await username.edit("`" f"{output}" "`")


@register(outgoing=True, pattern=r"^\.resetalive$")
async def amireallyalivereset(ureset):
    """ For .resetalive command, reset the username in the .alive command. """
    global DEFAULTUSER
    DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
    await ureset.edit("`" "Berhasil menyetel ulang pengguna untuk alive!" "`")


CMD_HELP.update(
    {
        "sysd": ">`.sysd`" "\nUntuk: Menampilkan informasi sistem menggunakan neofetch.",
        "botver": ">`.botver`" "\nUntuk: Menampilkan versi userbot.",
        "pip": ">`.pip <module(s)>`" "\nUntuk: Melakukan pencarian modul pip.",
        "alive": ">`.alive`"
        "\nUntuk: Ketik .alive untuk melihat apakah bot Anda berfungsi atau tidak."
        "\n\n>`.aliveu <teks>`"
        "\nUntuk: Mengubah 'pengguna' di .alive menjadi teks yang Anda inginkan."
        "\n\n>`.resetalive`"
        "\nUntuk: Menyetel ulang pengguna ke default.",
    }
)
