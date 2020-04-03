# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot start point """

from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from userbot import LOGS, bot


INVALID_PH = ('\nERROR: The Phone No. entered is INVALID'
              '\n Tip: Use Country Code along with number.'
              '\n or check your phone number and try again !')

try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)

LOGS.info("This is a fallback ProjectBish UserBot")

if len(argv) not in (1, 3, 4):
    bot.disconnect()
else:
    bot.run_until_disconnected()
