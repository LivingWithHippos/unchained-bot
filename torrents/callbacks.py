import logging

from telegram.ext import CallbackQueryHandler

from torrents.constants import UNRESTRICT_TORRENT

logger = logging.getLogger(__name__)


def torrent_callback_handler(bot, update, chat_data):
    context = chat_data.get('context')
    if not context:
        message = "Error processing keyboard button."
        logger.info(f"Conflicting update: '{update.to_dict()}'. Chat data: {chat_data}")
        bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=message
        )
        # Notify telegram we have answered
        update.callback_query.answer(text='')
        return

    # Get user selection
    answer = update.callback_query.data
    if answer == UNRESTRICT_TORRENT:
        # pass the torrent links to the unrestricter
        update.callback_query.answer(text='Unrestricting the torrent link/s.. Please wait')
        torrent_data = context['data']['torrent']


torrent_callback = CallbackQueryHandler(torrent_callback_handler, pass_chat_data=True)
