# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module containing commands related to android"""

import asyncio
import re
import os
import time
import math
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests import get
from bs4 import BeautifulSoup

from userbot import (
    CMD_HELP, TEMP_DOWNLOAD_DIRECTORY, GOOGLE_CHROME_BIN, CHROME_DRIVER
)
from userbot.events import register
from userbot.modules.upload_download import humanbytes, time_formatter

GITHUB = 'https://github.com'
DEVICES_DATA = ('https://raw.githubusercontent.com/androidtrackers/'
                'certified-android-devices/master/by_device.json')


async def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def human_to_bytes(size):
    units = {"MB": 2**20, "GB": 2**30, "TB": 2**40}
    size = size.upper()
    if not re.match(r' ', size):
        size = re.sub(r'([KMGT]?B)', r' \1', size)
    number, unit = [string.strip() for string in size.split()]
    return int(float(number)*units[unit])


@register(outgoing=True, pattern="^.magisk$")
async def magisk(request):
    """ magisk latest releases """
    magisk_dict = {
        "Stable":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/master/stable.json",
        "Beta":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/master/beta.json",
        "Canary (Release)":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/canary/release.json",
        "Canary (Debug)":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/canary/debug.json"
    }
    releases = 'Latest Magisk Releases:\n'
    for name, release_url in magisk_dict.items():
        data = get(release_url).json()
        releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                    f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | ' \
                    f'[Uninstaller]({data["uninstaller"]["link"]})\n'
    await request.edit(releases)


@register(outgoing=True, pattern=r"^.device(?: |$)(\S*)")
async def device_info(request):
    """ get android device basic info from its codename """
    textx = await request.get_reply_message()
    device = request.pattern_match.group(1)
    if device:
        pass
    elif textx:
        device = textx.text
    else:
        return await request.edit("`Usage: .device <codename> / <model>`")
    try:
        found = get(DEVICES_DATA).json()[device]
    except KeyError:
        reply = f"`Couldn't find info about {device}!`\n"
    else:
        reply = f'Search results for {device}:\n\n'
        for item in found:
            brand = item['brand']
            name = item['name']
            codename = device
            model = item['model']
            reply += f'{brand} {name}\n' \
                f'**Codename**: `{codename}`\n' \
                f'**Model**: {model}\n\n'
    await request.edit(reply)


@register(outgoing=True, pattern=r"^.codename(?: |)([\S]*)(?: |)([\s\S]*)")
async def codename_info(request):
    """ search for android codename """
    textx = await request.get_reply_message()
    brand = request.pattern_match.group(1).lower()
    device = request.pattern_match.group(2).lower()
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(' ')[0]
        device = ' '.join(textx.text.split(' ')[1:])
    else:
        return await request.edit("`Usage: .codename <brand> <device>`")
    found = [
        i for i in get(DEVICES_DATA).json()
        if i["brand"].lower() == brand and device in i["name"].lower()
    ]
    if len(found) > 8:
        found = found[:8]
    if found:
        reply = f'Search results for {brand.capitalize()} {device.capitalize()}:\n\n'
        for item in found:
            brand = item['brand']
            name = item['name']
            codename = item['device']
            model = item['model']
            reply += f'{brand} {name}\n' \
                f'**Codename**: `{codename}`\n' \
                f'**Model**: {model}\n\n'
    else:
        reply = f"`Couldn't find {device} codename!`\n"
    await request.edit(reply)


@register(outgoing=True, pattern="^.pixeldl(?: |$)(.*)")
async def download_api(dl):
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.mkdir(TEMP_DOWNLOAD_DIRECTORY)
    await dl.edit("`Collecting information...`")
    URL = dl.pattern_match.group(1)
    URL_MSG = await dl.get_reply_message()
    if URL:
        pass
    elif URL_MSG:
        URL = URL_MSG.text
    else:
        await dl.edit("`Empty information...`")
        return
    if not re.findall(r'\bhttps?://download.*pixelexperience.*\.org\S+', URL):
        await dl.edit("`Invalid information...`")
        return
    await dl.edit("`Sending information...`")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {'download.default_directory': './'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER,
                              options=chrome_options)
    await dl.edit("`Getting information...`")
    driver.get(URL)
    driver.command_executor._commands["send_command"] = (
         "POST", '/session/$sessionId/chromium/send_command')
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': TEMP_DOWNLOAD_DIRECTORY
        }
    }
    driver.execute("send_command", params)
    md5_origin = driver.find_elements_by_class_name(
        'download__meta')[0].text.split('\n')[2].split(':')[1].strip()
    file_name = driver.find_elements_by_class_name(
        'download__meta')[0].text.split('\n')[1].split(':')[1].strip()
    file_path = TEMP_DOWNLOAD_DIRECTORY + file_name
    download = driver.find_elements_by_class_name("download__btn")[0]
    download.click()
    x = download.get_attribute('text').split()[-2:]
    file_size = human_to_bytes((x[0] + x[1]).strip('()'))
    await asyncio.sleep(5)
    start = time.time()
    display_message = None
    complete = False
    while complete is False:
        try:
            downloaded = os.stat(file_path + '.crdownload').st_size
        except Exception:
            downloaded = os.stat(file_path).st_size
            file_size = downloaded
        diff = time.time() - start
        percentage = downloaded / file_size * 100
        speed = round(downloaded / diff, 2)
        eta = round((file_size - downloaded) / speed)
        prog_str = "`Downloading...` | [{0}{1}] `{2}%`".format(
            "".join(["●" for i in range(
                    math.floor(percentage / 10))]),
            "".join(["○"for i in range(
                    10 - math.floor(percentage / 10))]),
            round(percentage, 2))
        current_message = (
            "`[DOWNLOAD]`\n\n"
            f"`{file_name}`\n"
            f"`Status`\n{prog_str}\n"
            f"`{humanbytes(downloaded)} of {humanbytes(file_size)}"
            f" @ {humanbytes(speed)}`\n"
            f"`ETA` -> {time_formatter(eta)}"
        )
        if round(diff % 10.00) == 0 and display_message != current_message or (
          downloaded == file_size):
            await dl.edit(current_message)
            display_message = current_message
        if downloaded == file_size:
            MD5 = await md5(file_path)
            if md5_origin == MD5:
                complete = True
            else:
                await dl.edit("`Download corrupt...`")
                os.remove(file_path)
                return
    await dl.respond(
        f"`{file_name}`\n\n"
        f"Successfully downloaded to `{file_path}`."
    )
    await dl.delete()
    return


@register(outgoing=True, pattern=r"^.specs(?: |)([\S]*)(?: |)([\s\S]*)")
async def devices_specifications(request):
    """ Mobile devices specifications """
    textx = await request.get_reply_message()
    brand = request.pattern_match.group(1).lower()
    device = request.pattern_match.group(2).lower()
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(' ')[0]
        device = ' '.join(textx.text.split(' ')[1:])
    else:
        return await request.edit("`Usage: .specs <brand> <device>`")
    all_brands = BeautifulSoup(
        get('https://www.devicespecifications.com/en/brand-more').content,
        'lxml').find('div', {
            'class': 'brand-listing-container-news'
        }).findAll('a')
    brand_page_url = None
    try:
        brand_page_url = [
            i['href'] for i in all_brands if brand == i.text.strip().lower()
        ][0]
    except IndexError:
        await request.edit(f'`{brand} is unknown brand!`')
    devices = BeautifulSoup(get(brand_page_url).content, 'lxml') \
        .findAll('div', {'class': 'model-listing-container-80'})
    device_page_url = None
    try:
        device_page_url = [
            i.a['href']
            for i in BeautifulSoup(str(devices), 'lxml').findAll('h3')
            if device in i.text.strip().lower()
        ]
    except IndexError:
        await request.edit(f"`can't find {device}!`")
    if len(device_page_url) > 2:
        device_page_url = device_page_url[:2]
    reply = ''
    for url in device_page_url:
        info = BeautifulSoup(get(url).content, 'lxml')
        reply = '\n**' + info.title.text.split('-')[0].strip() + '**\n\n'
        info = info.find('div', {'id': 'model-brief-specifications'})
        specifications = re.findall(r'<b>.*?<br/>', str(info))
        for item in specifications:
            title = re.findall(r'<b>(.*?)</b>', item)[0].strip()
            data = re.findall(r'</b>: (.*?)<br/>', item)[0]\
                .replace('<b>', '').replace('</b>', '').strip()
            reply += f'**{title}**: {data}\n'
    await request.edit(reply)


@register(outgoing=True, pattern=r"^.twrp(?: |$)(\S*)")
async def twrp(request):
    """ get android device twrp """
    textx = await request.get_reply_message()
    device = request.pattern_match.group(1)
    if device:
        pass
    elif textx:
        device = textx.text.split(' ')[0]
    else:
        return await request.edit("`Usage: .twrp <codename>`")
    url = get(f'https://dl.twrp.me/{device}/')
    if url.status_code == 404:
        reply = f"`Couldn't find twrp downloads for {device}!`\n"
        return await request.edit(reply)
    page = BeautifulSoup(url.content, 'lxml')
    download = page.find('table').find('tr').find('a')
    dl_link = f"https://dl.twrp.me{download['href']}"
    dl_file = download.text
    size = page.find("span", {"class": "filesize"}).text
    date = page.find("em").text.strip()
    reply = f'**Latest TWRP for {device}:**\n' \
        f'[{dl_file}]({dl_link}) - __{size}__\n' \
        f'**Updated:** __{date}__\n'
    await request.edit(reply)


CMD_HELP.update({
    "android":
    ">`.magisk`"
    "\nGet latest Magisk releases"
    "\n\n>`.device <codename>`"
    "\nUsage: Get info about android device codename or model."
    "\n\n>`.codename <brand> <device>`"
    "\nUsage: Search for android device codename."
    "\n\n>`.pixeldl` **<download.pixelexperience.org>**"
    "\nUsage: Download pixel experience ROM into your userbot server."
    "\n\n>`.specs <brand> <device>`"
    "\nUsage: Get device specifications info."
    "\n\n>`.twrp <codename>`"
    "\nUsage: Get latest twrp download for android device."
})
