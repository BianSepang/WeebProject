# Copyright (C) 2020 Aidil Aryanto.
# All rights reserved.

import asyncio
import os
import shutil
import time

import deezloader
from pylast import User
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.types import DocumentAttributeAudio

from userbot import (
    CMD_HELP,
    DEEZER_ARL_TOKEN,
    DEEZER_EMAIL,
    DEEZER_PASSWORD,
    LASTFM_USERNAME,
    TEMP_DOWNLOAD_DIRECTORY,
    bot,
    lastfm,
)
from userbot.events import register
from userbot.utils import progress
from userbot.utils.FastTelethon import upload_file


@register(outgoing=True, pattern=r"^\.smd (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit("`Error: No scrobbling data found.`")
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@SpotifyMusicDownloaderBot"
    try:
        await event.edit("`Getting Your Music`")
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Downloading...`")
            try:
                response = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=752979930)
                )
                msg = await bot.send_message(chat, track)
                respond = await response
                res = conv.wait_event(
                    events.NewMessage(incoming=True, from_users=752979930)
                )
                r = await res
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("`Unblock `@SpotifyMusicDownloaderBot` and retry`")
                return
            await bot.forward_messages(event.chat_id, respond.message)
        await event.client.delete_messages(conv.chat_id, [msg.id, r.id, respond.id])
        await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@SpotifyMusicDownloaderBot` is not responding or Song not found!.`"
        )


@register(outgoing=True, pattern=r"^\.net (?:(now)|(.*) - (.*))")
async def _(event):
    if event.fwd_from:
        return
    if event.pattern_match.group(1) == "now":
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        if playing is None:
            return await event.edit("`Error: No current scrobble found.`")
        artist = playing.get_artist()
        song = playing.get_title()
    else:
        artist = event.pattern_match.group(2)
        song = event.pattern_match.group(3)
    track = str(artist) + " - " + str(song)
    chat = "@WooMaiBot"
    link = f"/netease {track}"
    await event.edit("`Searching...`")
    try:
        async with bot.conversation(chat) as conv:
            await asyncio.sleep(2)
            await event.edit("`Processing... Please wait`")
            try:
                msg = await conv.send_message(link)
                response = await conv.get_response()
                respond = await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.reply("`Please unblock @WooMaiBot and try again`")
                return
            await event.edit("`Sending Your Music...`")
            await asyncio.sleep(3)
            await bot.send_file(event.chat_id, respond)
        await event.client.delete_messages(
            conv.chat_id, [msg.id, response.id, respond.id]
        )
        await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@WooMaiBot` is not responding or Song not found!.`"
        )


@register(outgoing=True, pattern=r"^\.mhb(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    d_link = event.pattern_match.group(1)
    if ".com" not in d_link:
        await event.edit("`Enter a valid link to download from`")
    else:
        await event.edit("`Processing...`")
    chat = "@MusicsHunterBot"
    try:
        async with bot.conversation(chat) as conv:
            try:
                msg_start = await conv.send_message("/start")
                response = await conv.get_response()
                msg = await conv.send_message(d_link)
                details = await conv.get_response()
                song = await conv.get_response()
                await bot.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.edit("`Unblock `@MusicsHunterBot` and retry`")
                return
            await bot.send_file(event.chat_id, song, caption=details.text)
            await event.client.delete_messages(
                conv.chat_id, [msg_start.id, response.id, msg.id, details.id, song.id]
            )
            await event.delete()
    except TimeoutError:
        return await event.edit(
            "`Error: `@MusicsHunterBot` is not responding or Song not found!.`"
        )


@register(
    outgoing=True, pattern=r"^\.deez (now|.+)( FLAC| MP3\_320| MP3\_256| MP3\_128)?"
)
async def _(event):
    """DeezLoader by @An0nimia. Ported for UniBorg by @SpEcHlDe"""
    if event.fwd_from:
        return

    strings = {
        "name": "DeezLoad",
        "arl_token_cfg_doc": "ARL Token for Deezer",
        "invalid_arl_token": "please set the required variables for this module",
        "wrong_cmd_syntax": "bruh, now i think how far should we go. please terminate my Session.",
        "server_error": "We're experiencing technical difficulties.",
        "processing": "`Downloading...`",
        "uploading": "`Uploading...`",
    }

    ARL_TOKEN = DEEZER_ARL_TOKEN

    if not any([ARL_TOKEN, DEEZER_EMAIL, DEEZER_PASSWORD]):
        await event.edit(strings["invalid_arl_token"])
        return

    try:
        if DEEZER_EMAIL and DEEZER_PASSWORD:
            loader = deezloader.Login(
                email=DEEZER_EMAIL,
                password=DEEZER_PASSWORD,
            )
        else:
            loader = deezloader.Login(arl=ARL_TOKEN)
    except Exception as er:
        await event.edit(str(er))
        return

    temp_dl_path = os.path.join(TEMP_DOWNLOAD_DIRECTORY, str(time.time()))
    if not os.path.exists(temp_dl_path):
        os.makedirs(temp_dl_path)

    required_link = event.pattern_match.group(1)
    required_qty = event.pattern_match.group(2)
    required_qty = required_qty.strip() if required_qty else "MP3_128"

    await event.edit(strings["processing"])

    if "spotify" in required_link:
        if "track" in required_link:
            required_track = loader.download_trackspo(
                required_link,
                output_dir=temp_dl_path,
                quality_download=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
            )
            await event.edit(strings["uploading"])
            await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

        elif "album" in required_link:
            reqd_albums = loader.download_albumspo(
                required_link,
                output_dir=temp_dl_path,
                quality_download=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
                make_zip=False,
            )
            await event.edit(strings["uploading"])
            for required_track in reqd_albums:
                await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

    elif "deezer" in required_link:
        if "track" in required_link:
            required_track = loader.download_trackdee(
                required_link,
                output_dir=temp_dl_path,
                quality_download=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
            )
            await event.edit(strings["uploading"])
            await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

        elif "album" in required_link:
            reqd_albums = loader.download_albumdee(
                required_link,
                output_dir=temp_dl_path,
                quality_download=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
                make_zip=False,
            )
            await event.edit(strings["uploading"])
            for required_track in reqd_albums:
                await upload_track(required_track, event)
            shutil.rmtree(temp_dl_path)
            await event.delete()

    elif "now" in required_link:
        playing = User(LASTFM_USERNAME, lastfm).get_now_playing()
        artist = str(playing.get_artist())
        song = str(playing.get_title())
        try:
            required_track = loader.download_name(
                artist=artist,
                song=song,
                output_dir=temp_dl_path,
                quality_download=required_qty,
                recursive_quality=True,
                recursive_download=True,
                not_interface=True,
            )
        except BaseException as err:
            await event.edit(f"**ERROR :** {err}")
            await asyncio.sleep(5)
            await event.delete()
            return
        await event.edit(strings["uploading"])
        await upload_track(required_track, event)
        shutil.rmtree(temp_dl_path)
        await event.delete()

    else:
        await event.edit(strings["wrong_cmd_syntax"])


async def upload_track(track_location, message):
    duration = track_location.duration
    title = track_location.music
    performer = track_location.artist
    document_attributes = [
        DocumentAttributeAudio(
            duration=duration,
            voice=False,
            title=title,
            performer=performer,
            waveform=None,
        )
    ]
    c_time = time.time()
    track_path = track_location.song_path
    track_name = os.path.basename(track_path)
    with open(track_path, "rb") as f:
        result = await upload_file(
            client=message.client,
            file=f,
            name=track_name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, message, c_time, "[UPLOAD]", track_location)
            ),
        )
    await message.client.send_file(
        message.chat_id,
        result,
        caption=track_name,
        force_document=False,
        supports_streaming=True,
        allow_cache=False,
        attributes=document_attributes,
    )
    os.remove(track_path)


CMD_HELP.update(
    {
        "getmusic": ">`.smd` <artist - title>"
        "\nUsage: Download music from spotify use `@SpotifyMusicDownloaderBot`.\n\n"
        ">`.smd now`"
        "\nUsage: Download current LastFM scrobble use `@SpotifyMusicDownloaderBot`.\n\n"
        ">`.net` <artist - title>"
        "\nUsage: Download music use `@WooMaiBot`.\n\n"
        ">`.net now`"
        "\nUsage: Download current LastFM scrobble use `@WooMaiBot`.\n\n"
        ">`.mhb <spotify/deezer Link>`"
        "\nUsage: Download music from Spotify or Deezer use `@MusicsHunterBot`.\n\n"
        ">`.deez` <spotify/deezer link> FORMAT\n"
        "Usage: Download music from deezer or spotify.\n\n"
        ">`.deez now` FORMAT\n"
        "Usage: Download current LastFM scrobble using deezloader.\n"
        "Format (optional): `FLAC`, `MP3_320`, `MP3_256`, `MP3_128`."
    }
)
