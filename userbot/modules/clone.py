# Ported from Userge-Plugins

import asyncio
import os

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto

from userbot import CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register

PHOTO = TEMP_DOWNLOAD_DIRECTORY + "profile_pic.jpg"
USER_DATA = {}


@register(pattern=r"^\.clone(?: |$)(.*)", outgoing=True)
async def clone(cloner):
    """Clone first name, last name, bio and profile picture"""
    reply_message = cloner.reply_to_msg_id
    message = await cloner.get_reply_message()
    if reply_message:
        input_ = message.sender.id
    else:
        input_ = cloner.pattern_match.group(1)

    if not input_:
        await cloner.edit("`Please reply to user or input username`")
        await asyncio.sleep(5)
        await cloner.delete()
        return

    await cloner.edit("`Cloning...`")

    try:
        user = await cloner.client(GetFullUserRequest(input_))
    except ValueError:
        await cloner.edit("`Invalid username!`")
        await asyncio.sleep(2)
        await cloner.delete()
        return
    me = await cloner.client.get_me()

    if USER_DATA or os.path.exists(PHOTO):
        await cloner.edit("`First revert!`")
        await asyncio.sleep(2)
        await cloner.delete()
        return
    mychat = await cloner.client(GetFullUserRequest(me.id))
    USER_DATA.update(
        {
            "first_name": mychat.user.first_name or "",
            "last_name": mychat.user.last_name or "",
            "about": mychat.about or "",
        }
    )
    await cloner.client(
        UpdateProfileRequest(
            first_name=user.user.first_name or "",
            last_name=user.user.last_name or "",
            about=user.about or "",
        )
    )
    if not user.profile_photo:
        await cloner.edit("`User not have profile photo, cloned name and bio...`")
        await asyncio.sleep(5)
        await cloner.delete()
        return
    await cloner.client.download_profile_photo(user.user.id, PHOTO)
    await cloner.client(
        UploadProfilePhotoRequest(file=await cloner.client.upload_file(PHOTO))
    )
    await cloner.edit("`Profile is successfully cloned!`")
    await asyncio.sleep(3)
    await cloner.delete()


@register(pattern=r"^\.revert(?: |$)(.*)", outgoing=True)
async def revert_(reverter):
    """Returns Original Profile"""
    if not (USER_DATA or os.path.exists(PHOTO)):
        await reverter.edit("`Already reverted!`")
        await asyncio.sleep(2)
        await reverter.delete()
        return
    if USER_DATA:
        await reverter.client(UpdateProfileRequest(**USER_DATA))
        USER_DATA.clear()
    if os.path.exists(PHOTO):
        me = await reverter.client.get_me()
        photo = (await reverter.client.get_profile_photos(me.id, limit=1))[0]
        await reverter.client(
            DeletePhotosRequest(
                id=[
                    InputPhoto(
                        id=photo.id,
                        access_hash=photo.access_hash,
                        file_reference=photo.file_reference,
                    )
                ]
            )
        )
        os.remove(PHOTO)
    await reverter.edit("`Profile is successfully Reverted!`")
    await asyncio.sleep(3)
    await reverter.delete()


CMD_HELP.update(
    {
        "clone": ">`.clone` <reply to user>/<username>"
        "\nUsage: Clones someone names, profile picture, and bio"
        "\n\n>`.revert`"
        "\nUsage: Reverts back to your profile"
    }
)
