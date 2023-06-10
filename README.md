<p align="center"><a href="https://akkupy.me"><img src="https://github.com/akkupy/Sara-Bot/blob/main/Assets/Sara_Bot.jpg" width="5000"></a></p> 
<h1 align="center"><b>SARA-BOT  🇮🇳 </b></h1>
<h4 align="center">A Powerful, Smart And Simple Telegram Bot By Akku</h4>

> **Warning** <br>
> It Just Forwards the Movie or the file that is saved via /save command.Use it at your own risk .I'm not responsible for sharing copyrighted content with this program.


# KeyFeatures

* Movie Information Searching.
* Trailer Support.
* IMDB Links.
* Information On TV Series.


# Self-hosting (For Devs)

## Simply clone the repository and run the main file:
```sh
# Install Git First // (Else You Can Download And Upload to Your Local Server)
$ git clone https://github.com/akkupy/movie_bot
# Open Git Cloned File
$ cd movie_bot
# Config Virtual Env (Skip is already Done.)
$ virtualenv -p /usr/bin/python3 venv
$ . ./venv/bin/activate
# Install All Requirements.
$ pip(3) install -r requirements.txt
# Configure the .env file.
# Start Bot 
$ python(3) main.py
```

# Environment Variables
```
[+] If You Running Sara On A Deploy Services With Config Env Support Like Heroku, Zeet.co, Please Set "ENV" To True , Else For Self Host Services Like Digital Ocean Just Make A Credentials File And Put Vars Given Below.
    [-] BOT_API:   Telegram Bot Token 
    [-] OMDB_API :   OMDB Api Token
    [-] BOT_USERNAME : Telegram Bot Username
    [-] TMDB_API : TMDB Api Token
 
[+] The Sara will not work without setting the environment variables.
```


## An Example Of ".env" File
```

BOT_API = "sd78g6add897s8d7f875adad768d"
BOT_USERNAME = "akkubot"
OMDB_API = "d3w35frsd34scv"
TMDB_API = "dwa3r43rfsd344r4"
```


# Contact Me
 [![telegram](https://img.shields.io/badge/Akku-000000?style=for-the-badge&logo=telegram)](https://t.me/akkupy)


# License
[![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl-3.0.en.html)  

SaraBot is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 
