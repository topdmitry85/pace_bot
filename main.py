import os
import io
import gpxpy
import matplotlib.pyplot as plt
import numpy as np
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли мне .gpx-файл, и я посчитаю, насколько ровно ты бежал 🏃‍♂️📈")


async def handle_gpx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document

    if not document.file_name.endswith(".gpx"):
        await update.message.reply_text("Пожалуйста, пришли файл с расширением `.gpx`.")
        return

    file = await document.get_file()
    file_path = await file.download_to_drive()

    with open(file_path, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    distances = []
    times = []

    for track in gpx.tracks:
        for segment in track.segments:
            for i in range(1, len(segment.points)):
                p1 = segment.points[i - 1]
                p2 = segment.points[i]
                delta = p2.time - p1.time
                dt = delta.total_seconds()
                dist = p1.distance_3d(p2)
                if dt > 0 and dist > 0:
                    pace = (dt / 60) / (dist / 1000)  # мин/км
                    distances.append(dist)
