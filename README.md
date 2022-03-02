# WeebProject Userbot

<p align="center">
    <a href="https://app.codacy.com/gh/BianSepang/WeebProject/dashboard"> <img src="https://img.shields.io/codacy/grade/a723cb464d5a4d25be3152b5d71de82d?color=blue&logo=codacy&style=flat-square" alt="Codacy" /></a><br>
    <a href="https://github.com/BianSepang/WeebProject/stargazers"> <img src="https://img.shields.io/github/stars/BianSepang/WeebProject?logo=github&style=flat-square" alt="Stars" /></a>
    <a href="https://github.com/BianSepang/WeebProject/network/members"> <img src="https://img.shields.io/github/forks/BianSepang/WeebProject?logo=github&style=flat-square" alt="Forks" /></a>
    <a href="https://github.com/BianSepang/WeebProject/watchers"> <img src="https://img.shields.io/github/watchers/BianSepang/WeebProject?logo=github&style=flat-square" alt="Watch" /></a><br>
    <a href="https://github.com/BianSepang/WeebProject/graphs/contributors"> <img src="https://img.shields.io/github/contributors/BianSepang/WeebProject?color=blue&style=flat-square" alt="Contributors" /></a>
    <a href="https://pypi.org/project/Telethon/"> <img src="https://img.shields.io/pypi/v/telethon?label=telethon&logo=pypi&logoColor=white&style=flat-square" /></a>
</p>

```
#include <std/disclaimer.h>
/*
*    Your Telegram account may get banned.
*    I am not responsible for any improper use of this bot
*    This bot is intended for the purpose of having fun with memes,
*    as well as efficiently managing groups.
*    You ended up spamming groups, getting reported left and right,
*    and you ended up in a Finale Battle with Telegram and at the end
*    Telegram Team deleted your account?
*    And after that, then you pointed your fingers at us
*    for getting your acoount deleted?
*    I will be rolling on the floor laughing at you.
*/
```

A modular Telegram Userbot running on Python3 with sqlalchemy database.

based on [ProjectBish](https://github.com/adekmaulana/ProjectBish) Userbot
## Variable For Heroku Vars Settings
<details>
   <summary>Click for more details</summary>
   
**1. Required Variable name and value**
- `API_KEY` __# Get this value from [Telegram.org](https://my.telegram.org)__.
- `API_HASH` __# Get this value from [Telegram.org](https://my.telegram.org)__.
- `BOTLOG` __# Set to `False` to disable group logging. (Default `True`)__
- `BOTLOG_CHATID` __# Log chat id. Set it to `0` if BOTLOG = `False` and/or LOGSPAMMER = `False`__.
- `HEROKU_API_KEY` __# Get your Heroku API from [Heroku Account Settings](https://dashboard.heroku.com/account)__.
- `HEROKU_APP_NAME` __# Your Heroku app name which are deployed as userbot__.
- `LOGSPAMMER` __# Set this to `True` in case you want the error logs to be stored in the userbot log group. (requires a valid `BOTLOG_CHATID` to be set)__.
- `STRING_SESSION` __# Get this value by running [python3 string_session.py] in Termux or local system__.
- `TMP_DOWNLOAD_DIRECTORY` __# This variable for Download directory for many modules (GDrive, .download etc..)__.

**2. Non Mandatory Variable Name. [Recommended to fill this]**
- `ALIVE_NAME` __# Name to show in .alive message__.
- `ALIVE_LOGO` __# Show Image/Logo in .alive message. Use telegra.ph or any direct link image__.
- `ANTI_SPAMBOT` __# Kick spambots from groups after they join. (Requires admin permissions in group) fill this with `True` or `False`__
- `ANTI_SPAMBOT_SHOUT` __# Fill this value as false. if you're want Report spambots to @admins in groups after they join, just in case when you don't have admin powers to kick that shit by yourself__.
- `BIO_PREFIX` __# Prefix for Last.FM Module Bio__.
- `COUNTRY` __# Your Country to be used in the .time and .date commands__.
- `CLEAN_WELCOME` __# When a new person joins, the old welcome message is deleted, Set this to `True` or `False`__.
- `CONSOLE_LOGGER_VERBOSE` __# If you need verbosity on the console logging, set this `True` or `False`__.
- `DEEZER_ARL_TOKEN` __# Your DEEZER ARL TOKEN. If you don't know this, leave it blank__.
- `DEFAULT_BIO` __# Default you profile bio__.
- `G_DRIVE_DATA` __# Your client_secret.json__.
- `G_DRIVE_INDEX_URL` __# Your Cloudflare Google Drive Index URL__.
- `GENIUS_ACCESS_TOKEN` __# Client Access Token from [Genius](https://genius.com/api-clients) site__.
- `LASTFM_API` __# API Key for Last.FM module. Get one from [Last.FM](https://www.last.fm/api/account/create) site, Leave this blank if you won't use last.fm module__.
- `LASTFM_SECRET` __# SECRET Key for Last.FM module. Get one from [Last.FM](https://www.last.fm/api/account/create) site, Leave this blank if you won't use last.fm module__.
- `LASTFM_PASSWORD` __# Your last.fm password. Leave this blank if you won't use last.fm module__.
- `OPEN_WEATHER_MAP_APPID` __# Get your own API key from [Open Weather Map](https://openweathermap.org/api) site. Leave it blank if you won't use this__.
- `OCR_SPACE_API_KEY` __# OCR API Key for .ocr command. Get one from [OCR Space](https://ocr.space/ocrapi) site__.
- `PM_AUTO_BAN` __# PM shield if you won't any user spam your PM. Set this__ `True` __or__ `False`.
- `REM_BG_API_KEY` __# API Key for .rbg command. Get one from [remove.bg](https://www.remove.bg/api)__.
- `TZ_NUMBER` __# Fill `1` as a default value, Or in your country has multiple time zones. Just change the value to any time zones__.
- `TERM_ALIAS` __# Display user for .term command__.
- `UPSTREAM_REPO_URL` __# In case you're maintaining a fork repo, fill this with your fork repo url. if not, just leave this blank__.
- `USR_TOKEN_UPTOBOX` __# Uptobox API for uptobox direct link. Read [this](https://docs.uptobox.com/#how-to-find-my-api-token) (Required premium uptobox account)__.
- `WEATHER_DEFCITY` __# Set the default city for the userbot's weather module__.

</details>

# Deploy
**Heroku (GitHub Actions)**
1. Create github account and heroku account
2. Fork THIS repository [RECOMMEND TO ENABLE DEKSTOP MODE IN YOUR BROWSER]
3. Go to Your Gitub Forked repository settings. [[example pict]](https://telegra.ph/file/5f8e378f13f41ff7971de.jpg), Scroll down then Click Secret > actions
4. Fill All credentials required in Github secrets
- `HEROKU_API`. Fill your [Heroku api key](https://dashboard.heroku.com/account)
- `HEROKY_APP`. Fill your Heroku app name. **This name should only contain lowercase letters, numbers, and dashes.**
- `HEROKU_REGION`. Fill `us` or `en`
- `HEROKU_EMAIL`. Your heroku email
5. Now Go To Action tab in your repository [[example pict]](https://telegra.ph/file/28cecfc199fc34558ac91.jpg), Click Select Workflow [[example pict]](https://telegra.ph/file/5efd02314c3689bf149f3.jpg) Choose `Heroku Container build and push` Then Click Run Workflow from master branch [[example pict]](https://telegra.ph/file/b0afed12ff49f0ddf7c58.jpg). Wait process finish, if you got some errors while run workflow You can ask in [SUPPORT GROUP](https://t.me/+BYn1fSHCjHY5M2E1)
6. After deploy is finished, go to your heroku resource app add heroku posgress, check pict below

<details>
  <summary>Heroku posgress</summary>

![Posgress](https://telegra.ph/file/d6ca4af1af08ba628ab1c.jpg)

</details>

**Using "Bare hands", using Git and Python3 -- on (Linux, macOS, and Android [via Termux])**
1. Clone this repository on your local machine and `cd` (or `chdir`, anti bloat guy) to it
2. Set up Python virtual environment named "venv" inside it (Requires `virtualenv` installed on the system)
  - `virtualenv venv`
  - Don't forget to activate the virtualenv: `. venv/bin/activate`
3. Set up database for the userbot, search Google on how to set up a local database (PostgreSQL is recommended)
4. Install the requirements: `pip3 install -r ./requirements.txt`
5. Edit `sample_config.env` and save it as `config.env`
  - Do not forget to fill in the `REQUIRED %%` values, or else the bot will not run
6. Run the bot: `bash ./exec.sh`
  - Protip: See what `bash ./exec.sh --help` tells you

**Docker**
1. Clone this repository on your local machine and `cd` (or `chdir`, anti bloat guy) to it
2. Edit `sample_config.env` and save it as `config.env`
  - Set `DATABASE_URL` to `postgresql://USERNAME:PASSWORD@db:5432/weebproject`
  - You should set `USERNAME` and `PASSWORD` too in `docker-compose.yml`
  - Do not forget to fill in the `REQUIRED %%` values, or else the bot will not run
3. Run docker: `docker-compose up`

##### ※ Those steps are probably possible to pull off on Windows but it's pretty much unknown (different file tree paradigm, directory conventions, PowerShell instead of BASH or ZSH) -- If you're on Windows, you'd be better off running this on WSL (or WSL2)
---
## Credits
* [Adek Maulana](https://github.com/adekmaulana) - ProjectBish
* [Mr. Miss](https://github.com/keselekpermen69) - UserButt
* [Move Angel](https://github.com/MoveAngel) - One4uBot
* [Aidil Aryanto](https://github.com/aidilaryanto) - ProjectDils
* [Alfianandaa](https://github.com/alfianandaa) - ProjectAlf
* [GengKapak](https://github.com/GengKapak) - DCLXVI

and [everyone](https://github.com/BianSepang/WeebProject/graphs/contributors) that makes this userbot awesome :D

## License
Licensed under [Raphielscape Public License](https://github.com/BianSepang/WeebProject/blob/master/LICENSE) - Version 1.d, February 2020
