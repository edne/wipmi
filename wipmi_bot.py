#!/usr/bin/env python3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from staticmap import StaticMap, CircleMarker
import requests


def query(q):
    r = requests.get('127.0.0.1', params={"q": q})
    data = r.json()
    return data


def generate_map(data):
    coords = [entry["gps"] for entry in data]
    map_file = "map.png"
    m = StaticMap(600, 600, 10, 10)
    for coord in coords:
        marker = CircleMarker(coord, "blue", 5)
        m.add_marker(marker)
    image = m.render()
    image.save(map_file)
    return map_file


def start(bot, update):
    update.message.reply_text('Ciao, dimmi una via!')


def help(bot, update):
    update.message.reply_text('TODO')


def default(bot, update):
    street = update.message.text
    data = query("{} Milano".format(street))
    if data:
        replay = "Cantieri:\n{}".format("\n".join([entry["details"]
                                                   for entry in data]))
        update.message.reply_text(replay)
        map_file = generate_map(data)
        update.message.reply_photo(photo=open(map_file, 'rb'))
    else:
        update.message.reply_text("Nessun cantiere nei paraggi")


def error(bot, update, error):
    print(update, error)


def main():
    updater = Updater("TOKEN")

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, default))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
