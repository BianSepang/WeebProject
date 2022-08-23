# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for kanging stickers or making new ones. Thanks @rupansh"""

import io
import math
import random
import urllib.request
from os import remove

from PIL import Image
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageMediaPhoto,
)

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, bot
from userbot.events import register
from userbot.utils import run_cmd

KANGING_STR = [
    "Eh... Koq bagus... aku curry ahhh :3",
    "Aku curry ya kakak :)",
    "Curry Sticker dulu yee kan",
    "ehh, mantep nih.....aku ambil ya kaka",
    "Bagus eaaaa....\nAmbil ahh....",
    "Ini Sticker aku ambil yaa\nDUARR!",
    "leh ugha ni Sticker\nCurry ahh~",
    "Pim Pim Pom!!!\nni Sticker punya aing sekarang hehe",
    "Bentar boss, ane curry dulu",
    "Ihh, bagus nih\nCurry ahh~",
    "Curry lagi yee kan.....",
    "CURRY TROSS!!!",
    "Curry Sticker ahh.....",
    "Curry dolo boss",
    "Swiper jangan mencurry",
]


@register(outgoing=True, pattern=r"^\.curry")
async def kang(args):
    """For .kang command, kangs stickers or creates new ones."""
    user = await bot.get_me()
    if not user.username:
        user.username = user.first_name
    message = await args.get_reply_message()
    photo = None
    emojibypass = False
    is_anim = False
    is_video = False
    emoji = None

    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif "image" in message.media.document.mime_type.split("/"):
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            photo = io.BytesIO()
            await bot.download_file(message.media.document, photo)
            if (
                DocumentAttributeFilename(file_name="sticker.webp")
                in message.media.document.attributes
            ):
                emoji = message.media.document.attributes[1].alt
                if emoji != "":
                    emojibypass = True
        elif "tgsticker" in message.media.document.mime_type:
            await args.edit(f"`{random.choice(KANGING_STR)}`")
            await bot.download_file(message.media.document, "AnimatedSticker.tgs")

            attributes = message.media.document.attributes
            for attribute in attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    emoji = attribute.alt

            emojibypass = True
            is_anim = True
            photo = 1
        elif "video" in message.media.document.mime_type:
            sticker_attr = [
                attr
                for attr in message.media.document.attributes
                if isinstance(attr, DocumentAttributeSticker)
            ]

            if not sticker_attr:
                await args.edit("`Converting...`")
                vid_sticker = await convert_webm(message)
                await args.edit(f"`{random.choice(KANGING_STR)}`")
            else:
                await args.edit(f"`{random.choice(KANGING_STR)}`")
                vid_sticker = await bot.download_media(message)
                emoji = sticker_attr[0].alt
                emojibypass = True

            is_video = True
            photo = 1
        else:
            return await args.edit("`Unsupported File!`")
    else:
        return await args.edit("`I can't kang that...`")

    if photo:
        splat = args.text.split()
        if not emojibypass:
            emoji = "🤔"
        pack = 1
        if len(splat) == 3:
            pack = splat[2]  # User sent both
            emoji = splat[1]
        elif len(splat) == 2:
            if splat[1].isnumeric():
                # User wants to push into different pack, but is okay with
                # thonk as emote.
                pack = int(splat[1])
            else:
                # User sent just custom emote, wants to push to default
                # pack
                emoji = splat[1]

        packname = f"a{user.id}_by_{user.username}_{pack}"
        packnick = f"@{user.username}'s kang pack Vol.{pack}"
        cmd = "/newpack"
        file = io.BytesIO()

        if is_video:
            packname += "_vid"
            packnick += " (Video)"
            cmd = "/newvideo"
        elif is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        else:
            image = await resize_photo(photo)
            file.name = "sticker.png"
            image.save(file, "PNG")

        response = urllib.request.urlopen(
            urllib.request.Request(f"http://t.me/addstickers/{packname}")
        )
        htmlstr = response.read().decode("utf8").split("\n")

        if (
            "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>."
            not in htmlstr
        ):
            async with bot.conversation("@Stickers") as conv:
                await conv.send_message("/addsticker")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packname)
                x = await conv.get_response()
                while "120" in x.text:
                    pack += 1
                    packname = f"a{user.id}_by_{user.username}_{pack}"
                    packnick = f"@{user.username}'s kang pack Vol.{pack}"
                    await args.edit(
                        "`Switching to Pack "
                        + str(pack)
                        + " due to insufficient space`"
                    )
                    await conv.send_message(packname)
                    x = await conv.get_response()
                    if x.text == "Invalid pack selected.":
                        await conv.send_message(cmd)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message(packnick)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        if is_anim:
                            await conv.send_file("AnimatedSticker.tgs")
                            remove("AnimatedSticker.tgs")
                        elif is_video:
                            await conv.send_file(vid_sticker, force_document=True)
                            remove(vid_sticker)
                        else:
                            file.seek(0)
                            await conv.send_file(file, force_document=True)
                        await conv.get_response()
                        await conv.send_message(emoji)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message("/publish")
                        if is_anim:
                            await conv.get_response()
                            await conv.send_message(f"<{packnick}>")
                        # Ensure user doesn't get spamming notifications
                        await conv.get_response()
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.send_message("/skip")
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        await conv.send_message(packname)
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        await conv.get_response()
                        # Ensure user doesn't get spamming notifications
                        await bot.send_read_acknowledge(conv.chat_id)
                        return await args.edit(
                            "`Sticker added in a Different Pack !"
                            "\nThis Pack is Newly created!"
                            f"\nYour pack can be found [here](t.me/addstickers/{packname})",
                            parse_mode="md",
                        )
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                elif is_video:
                    await conv.send_file(vid_sticker, force_document=True)
                    remove(vid_sticker)
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await args.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`"
                    )
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/done")
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
        else:
            await args.edit("`Brewing a new Pack...`")
            async with bot.conversation("@Stickers") as conv:
                await conv.send_message(cmd)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message(packnick)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                if is_anim:
                    await conv.send_file("AnimatedSticker.tgs")
                    remove("AnimatedSticker.tgs")
                elif is_video:
                    await conv.send_file(vid_sticker, force_document=True)
                    remove(vid_sticker)
                else:
                    file.seek(0)
                    await conv.send_file(file, force_document=True)
                rsp = await conv.get_response()
                if "Sorry, the file type is invalid." in rsp.text:
                    return await args.edit(
                        "`Failed to add sticker, use` @Stickers `bot to add the sticker manually.`"
                    )
                await conv.send_message(emoji)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message("/publish")
                if is_anim:
                    await conv.get_response()
                    await conv.send_message(f"<{packnick}>")
                # Ensure user doesn't get spamming notifications
                await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.send_message("/skip")
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                await conv.send_message(packname)
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)
                await conv.get_response()
                # Ensure user doesn't get spamming notifications
                await bot.send_read_acknowledge(conv.chat_id)

        await args.edit(
            "Curry Success!" f"\n[Klik Disini](t.me/addstickers/{packname})",
            parse_mode="md",
        )


async def resize_photo(photo):
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = (512, 512)
    if (image.width and image.height) < 512:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        image = image.resize(sizenew)
    else:
        image.thumbnail(maxsize)

    return image


@register(outgoing=True, pattern=r"^\.stkrinfo$")
async def get_pack_info(event):
    if not event.is_reply:
        return await event.edit("`I can't fetch info from nothing, can I ?!`")

    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        return await event.edit("`Reply to a sticker to get the pack details`")

    try:
        stickerset_attr = rep_msg.document.attributes[1]
        await event.edit("`Fetching details of the sticker pack, please wait..`")
    except BaseException:
        return await event.edit("`This is not a sticker. Reply to a sticker.`")

    if not isinstance(stickerset_attr, DocumentAttributeSticker):
        return await event.edit("`This is not a sticker. Reply to a sticker.`")

    get_stickerset = await bot(
        GetStickerSetRequest(
            stickerset=InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            ),
            hash=0,
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)

    OUTPUT = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )

    await event.edit(OUTPUT)


@register(outgoing=True, pattern=r"^\.getsticker$")
async def sticker_to_png(sticker):
    if not sticker.is_reply:
        await sticker.edit("`NULL information to fetch...`")
        return False

    img = await sticker.get_reply_message()
    if not img.document:
        await sticker.edit("`Reply to a sticker...`")
        return False

    sticker_attr = [
        attr
        for attr in img.document.attributes
        if isinstance(attr, DocumentAttributeSticker)
    ]

    if not sticker_attr:
        await sticker.edit("`This is not a sticker...`")
        return

    await sticker.edit("`Getting sticker...`")

    try:
        with io.BytesIO() as image:
            await img.download_media(file=image)
            img = Image.open(image)

        with io.BytesIO() as image:
            img.save(image, format="PNG")
            image.name = "sticker.png"
            image.seek(0)

            msg = await sticker.respond(file=image.getvalue())
            await msg.reply(file=image, force_document=True)
    except Exception as exc:
        await sticker.edit(f"**ERROR:** {exc}")
    else:
        await sticker.delete()


async def get_video_reso(video):
    output, _ = await run_cmd(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0",
            video,
        ]
    )
    width, height = output.decode("utf-8").split(",")
    return width, height


async def convert_webm(message, output="sticker.webm"):
    vid_input = await message.client.download_media(message, TEMP_DOWNLOAD_DIRECTORY)
    w, h = await get_video_reso(vid_input)
    w, h = (-1, 512) if h > w else (512, -1)
    output = output if output.endswith(".webm") else f"{output}.webm"
    await run_cmd(
        [
            "ffmpeg",
            "-i",
            vid_input,
            "-ss",
            "00:00:00",
            "-to",
            "00:00:02.900",
            "-c:v",
            "libvpx-vp9",
            "-vf",
            f"scale={w}:{h}",
            "-an",
            output,
        ]
    )
    remove(vid_input)
    return output


CMD_HELP.update(
    {
        "stickers": ">`.curry`"
        "\nUsage: Reply .curry to a sticker or an image to put it to your sticker pack."
        "\n\n>`.curry (emoji['s]]?` [number]?"
        "\nUsage: Curry the sticker/image to the specified pack. You can specify the emoji too. "
        "(Default: 🤔)"
        "\n\n>`.stkrinfo`"
        "\nUsage: Gets info about the sticker pack."
        "\n\n>`.getsticker`"
        "\nUsage: Reply to a sticker to get 'PNG' file of sticker."
    }
)
