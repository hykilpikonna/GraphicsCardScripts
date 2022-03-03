import asyncio
import os

import pygame
import uvicorn
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
    sounds.append(s)
    return {'message': 'sound played'}


@app.get('/stop')
async def stop():
    for s in sounds:
        s.stop()
    sounds.clear()
    return {'message': 'sound stopped'}


async def start_telegram():
    updater = Updater(token=TG_TOKEN)
    dispatcher: Dispatcher = updater.dispatcher
    bot = updater.bot

    dispatcher.add_handler(CommandHandler('stop', lambda a, b: asyncio.run(stop())))
    dispatcher.add_handler(CommandHandler('alarm', lambda a, b: asyncio.run(alarm())))

    print('Starting Telegram...')
    updater.start_polling()


if __name__ == '__main__':
    pygame.mixer.init()
    asyncio.run(start_telegram())
    uvicorn.run(app, host="0.0.0.0", port=8000)
