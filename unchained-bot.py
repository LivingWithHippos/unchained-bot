# python bot telegram imports
import json
import logging
# python imports
import time
from functools import wraps
from pathlib import Path

import telegram
from telegram import ChatAction
from telegram import MessageEntity
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater

import debrid.credentials as credentials
# unchained imports
import debrid.real_debrid_api as real_debrid
from debrid.constants import credentials_mode_private, credentials_mode_open

sleep_time = 5

bot_config_path = "config.json"

json_markdown_formatting = "```json\n{}\n```"

credentials_missing_message = "No credentials found, please go through the authentication process using the /login command"
parameter_missing_message = "One or more parameters are missing. Use /help to check the correct command syntax."

custom_keyboard = [['/help', '/login'],
                   ['/user', '/downloads'],
                   ['/torrents']]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)


def help_command(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the unchained-bot ⛓🔨️💥\n"
             " these are the available commands, and these [parameters] are optional:\n "
             "/login - to start the authentication process\n"
             "/help - to see the available commands\n"
             "/check URL [password] - to see if a file is available on the hoster (has issues)\n"
             "/unrestrict URL [password] -  to unrestrict a download link\n"
             "/magnet URL - to unrestrict a magnet\n"
             "/torrents [number] - returns the last five or [number] torrents\n"
             "/downloads [number] - returns the last five or [number] downloads\n"
    )


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Sorry, I didn't understand that command. Use /help to see a list of possible "
                                  "commands.",
                             reply_markup=reply_markup)


# def token(update, context):
#    save the personal token and add it to all the calls
#    context.bot.send_message(chat_id=update.effective_chat.id,
#                             text="Insert your personal Real-Debrid API token from https://real-debrid.com/apitoken")

# todo: change method name to avoid confusion with credentials.save_credentials
# step 3 of the login procedure
def save_credentials(update, context, device_code, verification_result):
    # Using the value of device_code, your application makes a direct POST request to the token endpoint,
    # with the following parameters:
    #
    #     client_id: the value of client_id provided by the call to the credentials endpoint
    #     client_secret: the value of client_secret provided by the call to the credentials endpoint
    #     code: the value of device_code
    #     grant_type: use the value "http://oauth.net/grant_type/device/1.0"
    verification_json = verification_result.json()
    client_id = verification_json["client_id"]
    client_secret = verification_json["client_secret"]

    result = credentials.get_token(client_id,
                                   client_secret,
                                   device_code)

    # The answer will be a JSON object with the following properties:
    #
    #     access_token
    #     expires_in: token validity period, in seconds
    #     token_type: "Bearer"
    #     refresh_token: token that only expires when your application rights are revoked by user

    if result.status_code != 200:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Error loading token")
        print(result.json())
        return

    refresh_json = result.json()

    credentials.save_credentials(client_id, client_secret, device_code, refresh_json["access_token"],
                                 refresh_json["refresh_token"])

    credentials.update_credentials_mode(credentials_mode_open)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Token obtained and saved, credentials mode set to open.",
                             reply_markup=reply_markup)


# step 2 of the login procedure
def wait_confirmation(update, context, device_code):
    time.sleep(sleep_time)
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

    verification_result = credentials.get_verification(device_code)

    while verification_result.status_code != 200:
        counter += 1
        if counter > 60:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Waited too long. Restart the login procedure.")
            print(verification_result.json())
            return

        time.sleep(sleep_time)

        # Your application's call to the credentials endpoint now returns a JSON object with the following properties:
        #
        #   client_id: a new client_id that is bound to the user
        #   client_secret
        #
        # Your application stores these values and will use them for later requests.

        verification_result = credentials.get_verification(device_code)
    # Go to step 3
    save_credentials(update, context, device_code, verification_result)


# step 1 of the login procedure
def login(update, context):
    # credentials are working and loaded. Should also refresh token if necessary
    if credentials.check_credentials():
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Credentials correctly loaded",
                                 reply_markup=reply_markup)
        return

    # credentials missing, start the authentication process

    # first step, ask for new credentials
    result = credentials.get_auth()
    device_code = result.json()["device_code"]

    # Second step, your application asks the user to go to the verification endpoint (provided by verification_url)
    # and to type the code provided by user_code.

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Go to " +
                                  result.json()["verification_url"] +
                                  " and paste the code")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=result.json()["user_code"])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Or directly visit " +
                                  result.json()["direct_verification_url"])
    wait_confirmation(update, context, device_code)


def user(update, context):
    user_info = real_debrid.api_user_get()
    # credentials error
    if user_info is None:
        missing_credentials(update, context)
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=user_info,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def check_file(update, context):
    file_status = None
    if len(context.args) < 2:
        file_status = real_debrid.api_unrestrict_check(context.args[0])
    else:
        file_status = real_debrid.api_unrestrict_check(context.args[0], password=context.args[1])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=file_status,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def stream_file(update, context):
    # todo: add this check to others handlers
    if len(context.args) < 1:
        missing_parameter(update, context)
        return

    file_stream = real_debrid.api_streaming_transcode(context.args[0])

    if file_stream is None:
        missing_credentials(update, context)
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=file_stream,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def unrestrict_file(update, context):
    file_data = None
    if len(context.args) < 2:
        file_data = real_debrid.api_unrestrict_link(context.args[0])
    else:
        file_data = real_debrid.api_unrestrict_link(context.args[0], password=context.args[1])
    # credentials error
    if file_data is None:
        missing_credentials(update, context)
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=file_data,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


# todo: check if it is normal that a list of restricted link is returned
#  optionally directly pass the links to the unrestrict function
def unrestrict_folder(update, context):
    folder_data = real_debrid.api_unrestrict_folder(context.args[0])
    # credentials error
    if folder_data is None:
        missing_credentials(update, context)
        return

    # for long lists of links the message may be too long
    if isinstance(folder_data, list):
        messages = []
        link_list = ""
        for link in folder_data:
            markdown_link = "[{}]({})\n".format(link, link)
            if len(link_list) + len(markdown_link) >= telegram.constants.MAX_MESSAGE_LENGTH:
                _length = len(markdown_link)
                messages.append(link_list)
                link_list = markdown_link
            else:
                link_list += markdown_link
        # should have at least one here
        messages.append(link_list)
        for message in messages:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=message,
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=folder_data,
                                 parse_mode=telegram.ParseMode.MARKDOWN_V2)


def downloads_list(update, context):
    dlist = None
    if len(context.args) > 0 and context.args[0].isnumeric():
        dlist = real_debrid.api_downloads_list(limit=context.args[0])
    else:
        dlist = real_debrid.api_downloads_list()
    # credentials error
    if dlist is None:
        missing_credentials(update, context)
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=dlist,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def torrents_list(update, context):
    # return a list of this json:
    # {
    #         "id": "string",
    #         "filename": "string",
    #         "hash": "string", // SHA1 Hash of the torrent
    #         "bytes": int, // Size of selected files only
    #         "host": "string", // Host main domain
    #         "split": int, // Split size of links
    #         "progress": int, // Possible values: 0 to 100
    # // Current status of the torrent: magnet_error, magnet_conversion, waiting_files_selection,
    # queued, downloading, downloaded, error, virus, compressing, uploading, dead
    #         "status": "downloaded"
    #         "added": "string", // jsonDate
    #         "links": [
    #             "string" // Host URL
    #         ],
    #         "ended": "string", // !! Only present when finished, jsonDate
    #         "speed": int, // !! Only present in "downloading", "compressing", "uploading" status
    #         "seeders": int // !! Only present in "downloading", "magnet_conversion" status
    #     }

    tlist = None
    if len(context.args) > 0 and context.args[0].isnumeric():
        tlist = real_debrid.api_torrents_list(limit=context.args[0])
    else:
        tlist = real_debrid.api_torrents_list()
    # credentials error
    if tlist is None:
        missing_credentials(update, context)
        return

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=tlist,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def add_magnet(update, context):
    response = real_debrid.api_add_magnet(context.args[0])
    # credentials error
    if response is None:
        missing_credentials(update, context)
        return
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=response,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def set_private_token(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please add the token after the command -> /set_token TOKEN",
                                 parse_mode=telegram.ParseMode.MARKDOWN_V2)
        return

    token_updated = credentials.set_private_token(context.args[0])
    if token_updated:
        setting_updated = credentials.update_credentials_mode(credentials_mode_private)
        if setting_updated:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Token added, api mode set to private token. Use /set_credentials_mode MODE to switch mode.",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Token added, couldn't set mode to private_token_api. Check logs.",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Couldn't add token to db. Check logs.",
                                 parse_mode=telegram.ParseMode.MARKDOWN_V2)


def set_credentials_mode(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please add either private or open after the command -> /set_credentials_mode [open|private]",
                                 parse_mode=telegram.ParseMode.MARKDOWN_V2)
        return

    if str(context.args[0]).find("private") >= 0:
        setting_updated = credentials.update_credentials_mode(credentials_mode_private)
        if setting_updated:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Api Mode set to private token.",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Error setting Api Mode to private token. Check the logs",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
        return

    if str(context.args[0]).find("open") >= 0:
        setting_updated = credentials.update_credentials_mode(credentials_mode_open)
        if setting_updated:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Api Mode set to open token.",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Error setting Api Mode to open source. Check the logs",
                                     parse_mode=telegram.ParseMode.MARKDOWN_V2)


def missing_credentials(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=credentials_missing_message,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


def missing_parameter(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=parameter_missing_message,
                             parse_mode=telegram.ParseMode.MARKDOWN_V2)


#####################
#   I START HERE    #
#####################

def main():
    # load the bot properties
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
            logger = logging.getLogger(__name__)
    else:
        print("Missing bot token file: " + bot_config_path)
        exit(1)

    # add the commands handlers

    help_handler = CommandHandler('help', help_command)
    dispatcher.add_handler(help_handler)

    login_handler = CommandHandler('login', login)
    dispatcher.add_handler(login_handler)

    api_user_handler = CommandHandler('user', user)
    dispatcher.add_handler(api_user_handler)

    api_set_token_handler = CommandHandler('set_token', set_private_token)
    dispatcher.add_handler(api_set_token_handler)

    api_set_credentials_mode_handler = CommandHandler('set_credentials_mode', set_credentials_mode)
    dispatcher.add_handler(api_set_credentials_mode_handler)

    # todo: add support for personal real debrid token
    # token_handler = CommandHandler('token', token)
    # dispatcher.add_handler(token_handler)
    # api_stream_transcode = CommandHandler('stream', stream_file, (Filters.text & Filters.entity(MessageEntity.URL)))
    # dispatcher.add_handler(api_stream_transcode)

    # note: maybe if I add the same command without filters after this I could catch the /check
    # command written the wrong way and advise the user
    api_file_check = CommandHandler('check', check_file, (Filters.text & Filters.entity(MessageEntity.URL)))
    dispatcher.add_handler(api_file_check)

    api_file_unrestrict = CommandHandler('unrestrict', unrestrict_file,
                                         (Filters.text & Filters.entity(MessageEntity.URL)))
    dispatcher.add_handler(api_file_unrestrict)

    api_folder_unrestrict = CommandHandler('folder', unrestrict_folder,
                                           (Filters.text & Filters.entity(MessageEntity.URL)))
    dispatcher.add_handler(api_folder_unrestrict)

    api_downloads_list = CommandHandler('downloads', downloads_list)
    dispatcher.add_handler(api_downloads_list)

    api_torrents_list = CommandHandler('torrents', torrents_list)
    dispatcher.add_handler(api_torrents_list)

    api_add_magnet = CommandHandler('magnet', add_magnet)
    dispatcher.add_handler(api_add_magnet)

    # This handler must be added last.
    # If you added it sooner, it would be triggered before the CommandHandlers had a chance to look at the update
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
