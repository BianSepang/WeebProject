# Copyright (C) 2021 Bian Sepang
# All Rights Reserved.
#

import nekos

from userbot import CMD_HELP
from userbot.events import register


@register(pattern=r"^\.hentai$", outgoing=True)
async def _(event):
    """Gets random hentai gif from nekos.py."""
    await event.edit("`Fetching from nekos...`")
    pic = nekos.img("random_hentai_gif")
    await event.client.send_file(
        event.chat_id,
        pic,
        caption=f"[Source]({pic})",
    )
    await event.delete()


@register(pattern=r"^\.pussy$", outgoing=True)
async def _(event):
    """Gets anime pussy gif from nekos.py."""
    await event.edit("`Fetching from nekos...`")
    pic = nekos.img("pussy")
    await event.client.send_file(
        event.chat_id,
        pic,
        caption=f"[Source]({pic})",
    )
    await event.delete()


@register(pattern=r"^\.cum$", outgoing=True)
async def _(event):
    """Gets anime cum gif from nekos.py."""
    await event.edit("`Fetching from nekos...`")
    pic = nekos.img("cum")
    await event.client.send_file(
        event.chat_id,
        pic,
        caption=f"[Source]({pic})",
    )
    await event.delete()


@register(pattern=r"^\.nsfwneko$", outgoing=True)
async def _(event):
    """Gets nsfw neko gif from nekos.py."""
    await event.edit("`Fetching from nekos...`")
    pic = nekos.img("nsfw_neko_gif")
    await event.client.send_file(
        event.chat_id,
        pic,
        caption=f"[Source]({pic})",
    )
    await event.delete()


CMD_HELP.update(
    {
        "hentai": ">`.hentai`"
        "\nUsage: Gets random hentai gif from nekos"
        "\n\n>`.pussy`"
        "\nUsage: Gets anime pussy gif from nekos"
        "\n\n>`.cum`"
        "\nUsage: Gets anime cum gif from nekos"
        "\n\n>`.nsfwneko`"
        "\nUsage: Gets nsfw neko gif from nekos"
    }
)
