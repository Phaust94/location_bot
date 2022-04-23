"""
Bot main code
"""

import os
import sys

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler

cur_dir = os.path.dirname(__file__)
if cur_dir not in sys.path:
    sys.path.append(cur_dir)

from secrets import API_KEY
from version import __version__


def handle_location(update: Update, context: CallbackContext) -> None:
    print(update)
    loc = update.message.effective_attachment
    return None


def handle_error(update: Update, context: CallbackContext) -> None:
    errmsg = f"Error in chat {update.message.chat_id}: {{{context.error.__class__}}} {context.error}"
    print(errmsg)
    res_msg = "Я вас не зрозумів. Надішліть мені локацію!\nПомилка:"
    update.message.reply_text(f"{res_msg} {{{context.error.__class__}}} {context.error}")
    return None


# noinspection PyUnusedLocal
def handle_info(update: Update, context: CallbackContext) -> None:

    res = f"Квестовий бот для локації. Версія {__version__}"
    update.message.reply_text(res)

    return None


def main():
    updater = Updater(API_KEY, workers=1)

    updater.dispatcher.add_handler(MessageHandler(Filters.location, handle_location))
    updater.dispatcher.add_handler(CommandHandler("info", handle_info))

    updater.dispatcher.add_error_handler(handle_error)

    updater.start_polling()

    updater.idle()
    return None


if __name__ == '__main__':
    main()
