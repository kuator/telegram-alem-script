from io import BytesIO
import os
import random
import string
import mimetypes
import magic
import sqlite3
from PIL import Image, ImageDraw
from zoneinfo import ZoneInfo
import datetime
import requests
from pyrogram.methods.users import send_story
import asyncio
from pyrogram import Client
from dotenv import load_dotenv

load_dotenv()

connection = sqlite3.connect('db/my_database.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Post (
id INTEGER PRIMARY KEY,
post_id INTEGER
)
''')

connection.commit()

api_id=os.getenv('api_id')
api_hash=os.getenv('api_hash')
phone=os.getenv('phone')
text=os.getenv('text')
story_text=os.getenv('story_text')
chat_id=os.getenv('chat_id')
story_caption=os.getenv('story_caption')
channel=os.getenv('channel')
me=os.getenv('me')

async def new_daily_posts(app:Client):
    response = app.get_chat_history(channel, limit=2)
    daily_mic_posts = set()
    # new_daily_mic_posts = set()
    async for post in response:
        print(post)
        if post.caption and 'дневной микрофон' in post.caption.lower():
            daily_mic_posts.add(post.id)


    cursor.execute('SELECT * FROM Post')
    results = cursor.fetchall()
    old_posts = [result[1] for result in results]
    old_posts = set(old_posts)
    new_posts = list(daily_mic_posts - old_posts)
    return new_posts

async def process_daily_posts(app: Client, daily_posts):

    response = app.get_chat_history(channel, limit=2)

    async for post in response:
        if post.id not in daily_posts:
            continue

        file_id = post.document.file_id
        mimetype = post.document.mime_type
        file = await app.download_media(message=file_id, in_memory=True)

        file_bytes = bytes(file.getbuffer())

        file_name_no_extension = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        # ".png or .jpg"
        file_extension = mimetypes.guess_extension(mimetype)
        filename = file_name_no_extension

        if file_extension:
            filename = filename + file_extension

        with open(filename, 'wb') as writer:
            writer.write(file_bytes)

        result = await app.get_users(me)
        am_i_premium = result.is_premium

        await asyncio.sleep(2)

        if not am_i_premium:
            img = Image.open(filename)
            I1 = ImageDraw.Draw(img)
            I1.text((44, 1360), story_text, fill =(52, 143, 235), font_size=142, stroke_width=6, stroke_fill='black')
            img.save(filename)
            await app.send_story(photo=filename)
        else:
            await app.send_story(photo=filename, caption=story_caption)


        await app.send_message(chat_id=chat_id, text=text)
        cursor.execute('INSERT INTO Post (post_id) VALUES (?)', (post.id,))
        connection.commit()
        os.remove(filename)

async def main():

    async with Client("db/my_account", api_id, api_hash, phone_number=phone) as app:
        while True:
            daily_posts = await new_daily_posts(app)
            if not daily_posts:
                await asyncio.sleep(5)
                continue
            await process_daily_posts(app, daily_posts)
            await asyncio.sleep(5)
asyncio.run(main())

