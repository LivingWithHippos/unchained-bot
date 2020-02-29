# unchained-bot
![Python Version](https://img.shields.io/badge/python-3.5+-brightgreen)
[![Python-Wrapper Version](https://img.shields.io/badge/python--telegram--bot-12.4.2-blue)](https://github.com/python-telegram-bot/python-telegram-bot)


UnchainedBot is a [Telegram Bot](https://core.telegram.org/bots) that allows you to interface with [Real-Debrid](https://real-debrid.com/) (if you want to support me you can instead click through [this referral link](http://real-debrid.com/?id=78841)).

## Setup

##### 1. Create your telegram bot

Follow the [official instructions](https://core.telegram.org/bots#6-botfather) to chat with the BotFather, choose a name and a username and get your private token. 

##### 2. Get the repository

I use git:
```shell script
# clone this repo
git clone https://github.com/LivingWithHippos/unchained-bot.git
# move to the main folder
cd unchained-bot/debrid
# run main.py
python main.py
```
I don't use git:
* download [this repo](https://github.com/LivingWithHippos/unchained-bot) as a zip file ("Clone Or Download" on the right and then "Download ZIP")
* extract it somewhere

#####  3. Save your bot's token
 Create a file named `config.json` under the root directory (unchained-bot).
 Copy and paste this, using your token:
 
 ```json
{
  "bot_token": "Paste here your bot token, check https://core.telegram.org/bots#6-botfather"
}
```
You can alternatively copy, paste and rename the file `templates/template_config.json` and edit its content.

#####  3. Run the software

Install the following dependencies (a setup.py is under construction):
```shell script
beautifulsoup4
lxml
python-telegram-bot
requests
```
Move to the folder `debrid` and run `main.py` using you favourite method
```shell script
python main.py
```

If this is the first time your run it, talk to the bot (search for it using the username you chose in step 1) and use `/login` to start the login procedure.

**IMPORTANT:**
The bot will respond only as long as the software runs. My personal suggestion is to use a raspberry pi.

## Available Commands
The plan is to implement all the apis available [here](https://api.real-debrid.com/).

| Command  | Action  | Notes   |
|:---:|:---:|:---:|
| `/login`  | Start the login flow  | Usually needed only once, at the start  |
| `/user`  | Gives informations about the user  |   |
|  `/unrestrict link` | Unrestrict the `link`  |   |

##Development

UnchainedBot was made using Python 3.7, thanks to the wrapper [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

PRs are welcome.

#####Code state: ugly
<a href="https://ibb.co/s21dMZq"><img src="https://i.ibb.co/f2NzPsH/danger.png" width=100 alt="danger" border="0"></a>

The core of this software was coded in a single day, and python is not my strong suit. But for now "it just works".

##### Thanks, Mr. Unchained
<p align="center">
<a href="https://imgbb.com/"><img src="https://i.ibb.co/grzjQsT/Oliva.jpg" width=250 alt="Mr. Unchained" border="0"></a>
</p>