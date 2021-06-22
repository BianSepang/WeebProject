# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
"""Userbot help command"""

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.help(?: |$)(.*)")
async def help_handler(event):
    """For .help command."""
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit(f"`{args}` is not a valid module name.")
    else:
        head = "Please specify which module do you want help for !!"
        head2 = f"Loaded Modules : {len(CMD_HELP)}"
        head3 = "Usage: `.help` `<module name>`"
        head4 = "List for all available command below: "
        string = ""
        sep1 = "`••••••••••••••••••••••••••••••••••••••••••••••`"
        sep2 = "`=========================================`"
        for i in sorted(CMD_HELP):
            string += "`" + str(i)
            string += "`  |  "
        await event.edit(
            f"{head}\
              \n{head2}\
              \n{head3}\
              \n{sep2}\
              \n{head4}\
              \n\n{string}\
              \n{sep1}"
        )
