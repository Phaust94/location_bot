"""
Bot main code
"""

import os
import sys

import telegram.error
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


def _handle_point(update: Update, pt: Point, add_neighbours: bool = False) -> None:
    hash_ = pt.hash
    msg = f"Ваш секретний код - {hash_}"
    update.message.reply_text(msg)
    if add_neighbours:
        nb_hashes = set(x.hash for x in pt.neighbours(ACCURACY_METERS))
        nb_hashes = nb_hashes.union([pt.hash])
        nb_hashes_str = ", ".join(nb_hashes)
        msg = f"Сусіди: {nb_hashes_str}"
        update.message.reply_text(msg)
    return None


def _handle_coordinate(msg: str, update: Update, add_neighbours: bool = False):
    pts = msg.split(",")
    errmsg = "Це - не координати! Я очікую координати в форматі ##.######,##.######"
    if len(pts) != 2:
        raise ValueError(errmsg)
    try:
        lat, lon = list(map(float, pts))
    except Exception:
        raise ValueError(errmsg)

    loc = MyLocation(lat, lon)
    pt = Point.from_tg_location(loc)
    _handle_point(update, pt, add_neighbours)

    return None


# noinspection PyUnusedLocal
def handle_coordinates(update: Update, context: CallbackContext) -> None:
    txt = update.message.text
    _handle_coordinate(txt, update)
    return None


def handle_error(update: Update, context: CallbackContext) -> None:
    errmsg = f"Error in chat {update.message.chat_id}: {{{context.error.__class__}}} {context.error}"
    print(errmsg)
    res_msg = "Я вас не зрозумів. Надішліть мені локацію чи координати!\nПомилка:"
    msg = f"{res_msg} {{{context.error.__class__}}} {context.error}"
    if context.error.__class__ is telegram.error.TimedOut:
        msg += "\nСпробуйте повторити те ж саме ще раз!"
    update.message.reply_text(msg)
    return None


# noinspection PyUnusedLocal
def handle_info(update: Update, context: CallbackContext) -> None:

    res = f"Квестовий бот для локації. Версія {__version__}"
    update.message.reply_text(res)

    return None


# noinspection PyUnusedLocal
def handle_neighbours(update: Update, context: CallbackContext) -> None:

    msg = update.message.text
    msg = msg.lstrip("/nb")
    _handle_coordinate(msg, update, True)

    return None


def main():
    updater = Updater(API_KEY, workers=4)

    updater.dispatcher.add_handler(MessageHandler(Filters.location, handle_location))
    updater.dispatcher.add_handler(CommandHandler("info", handle_info))
    updater.dispatcher.add_handler(CommandHandler("nb", handle_neighbours))

    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_coordinates))

    updater.dispatcher.add_error_handler(handle_error)

    updater.start_polling()

    updater.idle()
    return None


if __name__ == '__main__':
    main()
