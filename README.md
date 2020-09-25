# unchained-bot
![Python Version](https://img.shields.io/badge/python-3.5+-brightgreen)
[![Python-Wrapper Version](https://img.shields.io/badge/python--telegram--bot-12.8-blue)](https://github.com/python-telegram-bot/python-telegram-bot)


UnchainedBot is a [Telegram Bot](https://core.telegram.org/bots) that allows you to interface with [Real-Debrid](https://real-debrid.com/). If you want to support me, you can instead click through [this referral link](http://real-debrid.com/?id=78841).

I also realized and are actively developing [Unchained for Android,](https://github.com/LivingWithHippos/unchained-android) which the same features and more.


- [unchained-bot](#unchained-bot)
  * [Setup](#setup)
    + [1. Get the repository](#1-get-the-repository)
    + [2. Setup your Telegram bot](#2-setup-your-telegram-bot)
      - [Save your bot's token](#save-your-bot-s-token)
      - [Restricting the bot access (optional)](#restricting-the-bot-access--optional-)
    + [3. Install the software](#3-install-the-software)
      - [Dockerfile (recommended)](#dockerfile--recommended-)
      - [Automatic install with pipenv (recommended)](#automatic-install-with-pipenv--recommended-)
      - [Automatic install with setup.py](#automatic-install-with-setuppy)
      - [Manual install](#manual-install)
    + [4. Bot initialization](#4-bot-initialization)
  * [Available Commands](#available-commands)
    + [Bot commands](#bot-commands)
    + [Real-Debrid API commands](#real-debrid-api-commands)
  * [Development](#development)
    + [API Parser](#api-parser)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

## Setup

### 1. Get the repository

Use git:
```shell script
# clone this repo
git clone https://github.com/LivingWithHippos/unchained-bot.git
```
Don't use git:
* download this repository as a zip file ("Clone Or Download" on the right and then "Download ZIP")
* extract it somewhere

### 2. Setup your Telegram bot

Follow the [official instructions](https://core.telegram.org/bots#6-botfather) to chat with the BotFather, choose a name, a username, and get your bot's token. 


#### Save your bot's token
 Create a file named `config.json` under the root directory of the repository (unchained-bot).
 Copy and paste this, using your token:
 
 ```json
{
  "bot_token": "Paste here your bot token, check https://core.telegram.org/bots#6-botfather"
}
```
You can alternatively copy and paste the file `templates/config.json` and edit its content.

#### Restricting the bot access (optional)

It is possible to lock the bot, so it only converses with a single user. You can run it withouth this option and then use `/get_id` to discover your telegram user id, or use other bots to discover it. 

Copy-paste it into your `config.json` file like this, without quotes:

 ```json
{
  "bot_token": "Paste here your bot token, check https://core.telegram.org/bots#6-botfather",
  "allowed_user": 12345678
}
```

If you don't want to restrict the access remove the "allowed_user" line in config.json

Restarting the bot will update the allowed user id with this value.

###  3. Install the software

Either use [Docker](https://www.docker.com/) or Python > 3.4. 

**IMPORTANT:**
The bot will respond only as long as the software runs. My suggestion is to use a raspberry pi.

#### Dockerfile (recommended)

After configuring the `config.json` file, run 

`docker build -t unchained-bot .`

to build the docker image and then 

`docker run unchained-bot`

to execute it.

#### Automatic install with pipenv (recommended)

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

**Note about pipenv:** minimum python version [is not supported](https://github.com/pypa/pipenv/issues/1050) by `pipenv` so I put `python_version = "3"` in Pipfile. This value means any version 3.x of Python will be considered acceptable, but to run unchained-bot, you need a version >=3.4. It also won't work with any version >=4, but at the moment, this avoids Python 2.x, which is the most probable "wrong version."

#### Automatic install with setup.py

Use `pip3` to install from setup.py
```shell script
# install the dependencies (mind the dot at the end)
pip3 install .
# wait for everything to be installed and then start the bot
python3 unchained-bot.py
```


#### Manual install

- Install the following dependencies:

```shell script
python-telegram-bot
requests
```

- Run `unchained-bot.py` using your favourite method
```shell script
python3 unchained-bot.py
```

###  4. Bot initialization

__IMPORTANT:__ Beside the configuration in `config.json`, the first time you run the bot (search for it using the username you chose in [step 1](#1-create-your-telegram-bot)) you need to use `/login` to start the login procedure or `/set_token YOUR_TOKEN` to configure the access to the real-debrid's API.

## Available Commands

Parameters between [square brackets] are optional.

### Bot commands

| Command  | Action  | Notes   |
|:---:|:---:|:---:|
| `/help`  | Shows a message similar to this table  |  |
| `/login`  | Start the login flow  | Usually needed only once, at the start  |
| `/set_token`  | Set the private API token  | with /login the app is allowed only on the following scopes: unrestrict, torrents, downloads, user |
| `/set_credentials_mode  mode`  | Set if the app should use the private or public token  | mode = `open` or `private`. Automatically switched by `/set_token` or by completing `/login` |
|  `/get_id` | Returns the user telegram id to be used for locking the bot access.  |   |

### Real-Debrid API commands

The plan is to implement all the APIs available [here](https://api.real-debrid.com/).

| Command  | Action  | Notes   |
|:---:|:---:|:---:|
| `/user`  | Gives information about the user  |   |
|  `/unrestrict link` [password] | Unrestrict the `link`  |   |
|  `/stream id` | Return the streaming options for `id`  | `id` is a field shown when a link is streamable. Unrestrict it first.  |
|  `/check link` [password] | Check if the `link` is available on the hoster.  | Apparently this API does not work |
|  `/folder folder_link` | Returns all the files in the folder `folder_link`.  |   |
|  `/downloads [number]` | Returns the last five or [number] downloads.  |   |
|  `/torrents [number]` | Returns the last five or [number] torrents.  |   |
|  `/magnet magnet_link` | Add `magnet_link` to the torrents.  |   |

## Development

UnchainedBot was made using Python 3.7, thanks to the wrapper [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and with Pycharm as IDE.

You can check the project page to see the roadmap and what's happening.

PRs are welcome.

### API Parser


To speed up the creation of function talking to Real Debid's APIs, I wrote a parser. It reads the content of https://api.real-debrid.com/ and saves it in a more structured form easier to operate on.

Install the dependencies

```shell script
beautifulsoup4
lxml
```

And run it with:

`python3 api_parser/api_page_parser.py` 

which will save a file under the `parsed` folder. A `parsed_api.json` should already be available

#### Code state: ugly

<a href="https://ibb.co/s21dMZq"><img src="https://i.ibb.co/f2NzPsH/danger.png" width=150 alt="danger" border="0"></a>

I coded the core of this software in a single day, and python is not my strong suit. But for now, "it just works."

### Thanks, Mr. Unchained
<a href="https://imgbb.com/"><img src="https://i.ibb.co/grzjQsT/Oliva.jpg" width=300 alt="Mr. Unchained" border="0"></a>
