import os

from fastapi import FastAPI
from pygame.mixer import Sound
from telegram.ext import Updater, Dispatcher, CommandHandler

# Config
AUDIO = 'alarm.mp3'
TG_TOKEN = os.environ['TG_TOKEN']

# Internal variables
app = FastAPI()
sounds: list[Sound] = []


@app.get('/alarm')
async def alarm():
    s = Sound(AUDIO)
    s.play()
    return {'message': 'sound played'}


@app.get('/stop')
async def stop():
    for s in sounds:
        s.stop()
    sounds.clear()


if __name__ == '__main__':
    updater = Updater(token=TG_TOKEN)
    dispatcher: Dispatcher = updater.dispatcher
    bot = updater.bot

    dispatcher.add_handler(CommandHandler('stop', stop))
    dispatcher.add_handler(CommandHandler('alarm', alarm))

    print('Starting...')
    updater.start_polling()
