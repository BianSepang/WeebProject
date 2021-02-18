# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for executing code and terminal commands from Telegram. """

import asyncio
import io
import re
import sys
import traceback
from os import remove
from sys import executable

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, TERM_ALIAS
from userbot.events import register


@register(outgoing=True, pattern=r"^\.eval(?: |$|\n)([\s\S]*)")
async def _(event):
    if event.fwd_from:
        return
    s_m_ = await event.edit("Processing ...")
    cmd = event.pattern_match.group(1)
    if not cmd:
        return await s_m_.edit("`What should i eval...`")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        returned = await aexec(cmd, s_m_)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = "No Output"
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    elif returned:
        evaluation = returned

    final_output = "**EVAL**: \n`{}` \n\n**OUTPUT**: \n`{}` \n".format(cmd, evaluation)

    if len(final_output) >= 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await s_m_.reply(cmd, file=out_file)
            await event.delete()
    else:
        await s_m_.edit(final_output)


async def aexec(code, smessatatus):
    message = event = smessatatus

    reply = await event.get_reply_message()
    exec(
        f"async def __aexec(message, reply, client): "
        + "\n event = smessatatus = message"
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](message, reply, message.client)


@register(outgoing=True, pattern=r"^\.exec(?: |$|\n)([\s\S]*)")
async def run(run_q):
    """ For .exec command, which executes the dynamically created program """
    code = run_q.pattern_match.group(1)

    if run_q.is_channel and not run_q.is_group:
        return await run_q.edit("`Exec isn't permitted on channels!`")

    if not code:
        return await run_q.edit(
            "``` At least a variable is required to"
            "execute. Use .help exec for an example.```"
        )

    if code in ("userbot.session", "config.env"):
        return await run_q.edit("`That's a dangerous operation! Not Permitted!`")

    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = (
            clines[0] + "\n" + clines[1] + "\n" + clines[2] + "\n" + clines[3] + "..."
        )

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        executable,
        "-c",
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if result:
        if len(result) > 4096:
            file = open("output.txt", "w+")
            file.write(result)
            file.close()
            await run_q.client.send_file(
                run_q.chat_id,
                "output.txt",
                reply_to=run_q.id,
                caption="`Output too large, sending as file`",
            )
            remove("output.txt")
            return
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Result: **\n`" f"{result}" "`"
        )
    else:
        await run_q.edit(
            "**Query: **\n`" f"{codepre}" "`\n**Result: **\n`No result returned/False`"
        )

    if BOTLOG:
        await run_q.client.send_message(
            BOTLOG_CHATID, "Exec query " + codepre + " was executed successfully."
        )


@register(outgoing=True, pattern=r"^\.term(?: |$|\n)(.*)")
async def terminal_runner(term):
    """ For .term command, runs bash commands and scripts on your server. """
    curruser = TERM_ALIAS
    command = term.pattern_match.group(1)
    try:
        from os import geteuid

        uid = geteuid()
    except ImportError:
        uid = "This ain't it chief!"

    if term.is_channel and not term.is_group:
        return await term.edit("`Term commands aren't permitted on channels!`")

    if not command:
        return await term.edit(
            "``` Give a command or use .help term for an example.```"
        )

    for i in ("userbot.session", "env"):
        if command.find(i) != -1:
            return await term.edit("`That's a dangerous operation! Not Permitted!`")

    if not re.search(r"echo[ \-\w]*\$\w+", command) is None:
        return await term.edit("`That's a dangerous operation! Not Permitted!`")

    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Output too large, sending as file`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID,
            "Terminal command " + command + " was executed sucessfully.",
        )


CMD_HELP.update(
    {
        "eval": ">`.eval print('world')`" "\nUsage: Just like exec.",
        "exec": ">`.exec print('hello')`" "\nUsage: Execute small python scripts.",
        "term": ">`.term <cmd>`"
        "\nUsage: Run bash commands and scripts on your server.",
    }
)
