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

- Install the following dependencies (a setup.py is under construction):

```shell script
python-telegram-bot
requests
```
If you are going to use the [API parser,](#api-parser) you'll also need

```shell script
beautifulsoup4
lxml
```

- Run `unchained-bot.py` using your favourite method
```shell script
python unchained-bot.py
```

If this your first time running it, talk to the bot (search for it using the username you chose in [step 1](#1-create-your-telegram-bot)) and use `/login` to start the login procedure.

**IMPORTANT:**
The bot will respond only as long as the software runs. My suggestion is to use a raspberry pi.

## Available Commands
The plan is to implement all the APIs available [here](https://api.real-debrid.com/).

| Command  | Action  | Notes   |
|:---:|:---:|:---:|
| `/login`  | Start the login flow  | Usually needed only once, at the start  |
| `/user`  | Gives information about the user  |   |
|  `/unrestrict link` | Unrestrict the `link`  |   |

## Development

UnchainedBot was made using Python 3.7, thanks to the wrapper [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

PRs are welcome.

### API Parser


To speed up the creation of function talking to Real Debid's APIs, I wrote a parser. It reads the content of https://api.real-debrid.com/ and saves it in a more structured form.
It can be used with:

`python api_parser/api_page_parser.py` 

that will save a file under the `parsed` folder. A `parsed_api.json` should already be available

#### Code state: ugly

<a href="https://ibb.co/s21dMZq"><img src="https://i.ibb.co/f2NzPsH/danger.png" width=150 alt="danger" border="0"></a>

I coded the core of this software in a single day, and python is not my strong suit. But for now, "it just works."

### Thanks, Mr. Unchained
<a href="https://imgbb.com/"><img src="https://i.ibb.co/grzjQsT/Oliva.jpg" width=300 alt="Mr. Unchained" border="0"></a>
