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

## Deploy
### Heroku
Click this button below to Deploy to Heroku
<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/BianSepang/WeebProject/tree/master"> <img src="https://www.herokucdn.com/deploy/button.png" alt="Deploy to Heroku"/></a></p>

### "Bare hands", using Git and Python3 -- on (Linux, macOS, and Android [via Termux])
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
