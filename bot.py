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

from secrets import API_KEY, ADMIN_ID
from version import __version__
from helpers import Point, MyLocation
from constants import ACCURACY_METERS


# noinspection PyUnusedLocal
def handle_location(update: Update, context: CallbackContext) -> None:
    loc = update.message.effective_attachment
    pt = Point.from_tg_location(loc)
    _handle_point(update, pt)
    return None


def _handle_point(update: Update, pt: Point) -> None:
    hash_ = pt.hash
    msg = f"Ваш секретний код - {hash_}"
    update.message.reply_text(msg)
    if update.message.chat_id == ADMIN_ID:
        nb_hashes = set(x.hash for x in pt.neighbours(ACCURACY_METERS))
        nb_hashes = nb_hashes.union([pt.hash])
        nb_hashes_str = ", ".join(nb_hashes)
        msg = f"Сусіди: {nb_hashes_str}"
        update.message.reply_text(msg)
    return None


# noinspection PyUnusedLocal
def handle_coordinates(update: Update, context: CallbackContext) -> None:
    txt = update.message.text
    pts = txt.split(",")
    errmsg = "Це - не координати! Я очікую координати в форматі ##.######,##.######"
    if len(pts) != 2:
        raise ValueError(errmsg)
    try:
        lat, lon = list(map(float, pts))
    except Exception:
        raise ValueError(errmsg)

    loc = MyLocation(lat, lon)
    pt = Point.from_tg_location(loc)
    _handle_point(update, pt)
    return


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
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_coordinates))
    updater.dispatcher.add_handler(CommandHandler("info", handle_info))

    updater.dispatcher.add_error_handler(handle_error)

    updater.start_polling()

    updater.idle()
    return None


if __name__ == '__main__':
    main()
