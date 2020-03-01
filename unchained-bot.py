import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import debrid.real_debrid_api as real_debrid
import time
from pathlib import Path
import json

rd = real_debrid.DebridApi
sleep_time = 5

bot_config_path = "config.json"

dispatcher = None
updater = None


def load_bot():
    global dispatcher
    global updater
    if Path(bot_config_path).is_file():
        with open(bot_config_path, 'r') as f:
            bot_data = json.load(f)
            my_token = bot_data["bot_token"]
            if my_token is None:
                print("Missing token in file: " + bot_config_path + "./nObtain one following instruction at "
                                                                    "https://core.telegram.org/bots#6-botfather")
                exit(1)

            updater = Updater(token=my_token, use_context=True)
            dispatcher = updater.dispatcher
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                level=logging.INFO)
    else:
        print("Missing bot token file: " + bot_config_path)
        exit(1)


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def token(update, context):
    rd.save_token(context.args)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Insert your personal Real-Debrid API token from https://real-debrid.com/apitoken")


def login(update, context):
    if real_debrid.check_credentials():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Credentials correctly loaded")
        return

    # using open source token
    result = real_debrid.get_auth()
    device_code = result.json()["device_code"]

    # Your application asks the user to go to the verification endpoint (provided by verification_url) and to type
    # the code provided by user_code.

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Go to " +
                                  result.json()["verification_url"] +
                                  " and paste the code")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=result.json()["user_code"])

    time.sleep(sleep_time * 2)
    counter = 0

    # Using the value of device_code, every 5 seconds your application starts making direct requests to the
    # credentials endpoint, with the following query string parameters:
    #
    # client_id
    # code: the value of device_code
    #
    # Your application will receive an error message until the user has entered the code and authorized the
    # application.

    # The user enters the code, and then logs in if they aren't logged in yet.

    # The user chooses to authorize your application, and can then close the browser window.

    verification_result = real_debrid.get_verification(device_code)

    while verification_result.status_code != 200:
        counter += 1
        if counter > 30:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Wait too long. Restart the login.")
            print(verification_result.json())
            return

        time.sleep(sleep_time)

        # Your application's call to the credentials endpoint now returns a JSON object with the following properties:
        #
        #   client_id: a new client_id that is bound to the user
        #   client_secret
        #
        # Your application stores these values and will use them for later requests.

        verification_result = real_debrid.get_verification(device_code)

    # Using the value of device_code, your application makes a direct POST request to the token endpoint,
    # with the following parameters:
    #
    #     client_id: the value of client_id provided by the call to the credentials endpoint
    #     client_secret: the value of client_secret provided by the call to the credentials endpoint
    #     code: the value of device_code
    #     grant_type: use the value "http://oauth.net/grant_type/device/1.0"

    client_id = verification_result.json()["client_id"]
    client_secret = verification_result.json()["client_secret"]

    result = real_debrid.get_token(client_id,
                                   client_secret,
                                   device_code)

    if result.status_code != 200:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Error loading token")
        print(result.json())
        return

    refresh_token = result.json()["refresh_token"]
    real_debrid.save_refresh_token(client_id, client_secret, refresh_token)

    # The answer will be a JSON object with the following properties:
    #
    #     access_token
    #     expires_in: token validity period, in seconds
    #     token_type: "Bearer"
    #     refresh_token: token that only expires when your application rights are revoked by user

    real_debrid.save_token_response(result.json())
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Token obtained and saved")


def user(update, context):
    user_info = real_debrid.api_user_get()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=user_info,
                             parse_mode=telegram.ParseMode.MARKDOWN)


def check_file(update, context):
    file_status = real_debrid.api_unrestrict_check(context.args[0])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=file_status,
                             parse_mode=telegram.ParseMode.MARKDOWN)


def unrestrict_file(update, context):
    file_data = real_debrid.api_unrestrict_link(context.args[0])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=file_data,
                             parse_mode=telegram.ParseMode.MARKDOWN)


def downloads_list(update, context):
    dlist = real_debrid.api_downloads_list(offset=0)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=dlist,
                             parse_mode=telegram.ParseMode.MARKDOWN)


def torrents_list(update, context):
    tlist = real_debrid.api_torrents_list()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=tlist,
                             parse_mode=telegram.ParseMode.MARKDOWN)


#####################
#   I START HERE    #
#####################

load_bot()

real_debrid.check_credentials()

token_handler = CommandHandler('token', token)
dispatcher.add_handler(token_handler)

login_handler = CommandHandler('login', login)
dispatcher.add_handler(login_handler)

api_user_handler = CommandHandler('user', user)
dispatcher.add_handler(api_user_handler)

api_file_check = CommandHandler('check', check_file)
dispatcher.add_handler(api_file_check)

api_file_unrestrict = CommandHandler('unrestrict', unrestrict_file)
dispatcher.add_handler(api_file_unrestrict)

api_downloads_list = CommandHandler('downloads', downloads_list)
dispatcher.add_handler(api_downloads_list)

api_torrents_list = CommandHandler('torrents', torrents_list)
dispatcher.add_handler(api_torrents_list)

updater.start_polling()
