# unchained-bot
![Python Version](https://img.shields.io/badge/python-3.5+-brightgreen)
[![Python-Wrapper Version](https://img.shields.io/badge/python--telegram--bot-12.4.2-blue)](https://github.com/python-telegram-bot/python-telegram-bot)


UnchainedBot is a [Telegram Bot](https://core.telegram.org/bots) that allows you to interface with [Real-Debrid](https://real-debrid.com/). If you want to support me, you can instead click through [this referral link](http://real-debrid.com/?id=78841).

- [unchained-bot](#unchained-bot)
  * [Setup](#setup)
      - [1. Create your telegram bot](#1-create-your-telegram-bot)
      - [2. Get the repository](#2-get-the-repository)
      - [3. Save your bot's token](#3-save-your-bot-s-token)
      - [4. Run the software](#4-run-the-software)
        * [Automatic install with pipenv (recomended)](#automatic-install-with-pipenv--recomended-)
        * [Automatic install with setup.py](#automatic-install-with-setuppy)
        * [Manual install](#manual-install)
  * [Available Commands](#available-commands)
  * [Development](#development)
    + [API Parser](#api-parser)

## Setup

#### 1. Create your telegram bot

Follow the [official instructions](https://core.telegram.org/bots#6-botfather) to chat with the BotFather, choose a name, a username, and get your private token. 

#### 2. Get the repository

Use git:
```shell script
# clone this repo
git clone https://github.com/LivingWithHippos/unchained-bot.git
```
Don't use git:
* download this repository as a zip file ("Clone Or Download" on the right and then "Download ZIP")
* extract it somewhere

####  3. Save your bot's token
 Create a file named `config.json` under the root directory of the repository (unchained-bot).
 Copy and paste this, using your token:
 
 ```json
{
  "bot_token": "Paste here your bot token, check https://core.telegram.org/bots#6-botfather"
}
```
You can alternatively copy and paste the file `templates/config.json` and edit its content.

####  4. Run the software

This part will assume you have python > 3.4 installed.

**IMPORTANT:**
The bot will respond only as long as the software runs. My suggestion is to use a raspberry pi.

##### Automatic install with pipenv (recomended)

If you do not have `pipenv` installed, follow [these instructions.](https://pipenv.readthedocs.io/en/latest/#install-pipenv-today) If you have `brew`,
just run `brew install pipenv`.

Now run from the root folder

```shell script
# install the dependencies
pipenv install
# launch the virtual environment
pipenv shell
# start the bot
python3 unchained-bot.py
```

**Note about pipenv:** minimum python version [is not supported](https://github.com/pypa/pipenv/issues/1050) by `pipenv` so I put `python_version = "3"` in Pipfile. This value means any version 3.x of Python will be considered acceptable, but to run unchained-bot, you need a version >=3.4. It also won't work with any version >=4, but at the moment, this avoids python 2.x, which is the most probable "wrong version."

##### Automatic install with setup.py

Use `pip3` to install from setup.py
```shell script
# install the dependencies (mind the dot at the end)
pip3 install .
# wait for eveything to be installed and then start the bot
python3 unchained-bot.py
```


##### Manual install

- Install the following dependencies:

```shell script
python-telegram-bot
requests
```

- Run `unchained-bot.py` using your favourite method
```shell script
python3 unchained-bot.py
```

If this your first time running it, talk to the bot (search for it using the username you chose in [step 1](#1-create-your-telegram-bot)) and use `/login` to start the login procedure.

## Available Commands
The plan is to implement all the APIs available [here](https://api.real-debrid.com/).

| Command  | Action  | Notes   |
|:---:|:---:|:---:|
| `/login`  | Start the login flow  | Usually needed only once, at the start  |
| `/user`  | Gives information about the user  |   |
|  `/unrestrict link` | Unrestrict the `link`  |   |
|  `/check link` | Check if the `link` is available on the hoster.  |   |
|  `/folder folder_link` | Returns all the files in the folder `folder_link`.  |   |
|  `/downloads` | Returns the last three downloads.  |   |
|  `/torrents` | Returns the last three torrents.  |   |
|  `/magnet magnet_link` | Add `magnet_link` to the torrents.  |   |

## Development

UnchainedBot was made using Python 3.7, thanks to the wrapper [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

PRs are welcome.

### API Parser


To speed up the creation of function talking to Real Debid's APIs, I wrote a parser. It reads the content of https://api.real-debrid.com/ and saves it in a more structured form easier to operate on.

Install the dependencies

```shell script
beautifulsoup4
lxml
```

And use it with:

`python3 api_parser/api_page_parser.py` 

that will save a file under the `parsed` folder. A `parsed_api.json` should already be available

#### Code state: ugly

<a href="https://ibb.co/s21dMZq"><img src="https://i.ibb.co/f2NzPsH/danger.png" width=150 alt="danger" border="0"></a>

I coded the core of this software in a single day, and python is not my strong suit. But for now, "it just works."

### Thanks, Mr. Unchained
<a href="https://imgbb.com/"><img src="https://i.ibb.co/grzjQsT/Oliva.jpg" width=300 alt="Mr. Unchained" border="0"></a>
