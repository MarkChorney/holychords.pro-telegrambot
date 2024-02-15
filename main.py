# import logging
import logging

# import Telegram API library aiogram
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# import database SQLite3
import sqlite3

# import to parse
from bs4 import BeautifulSoup
import requests
import re

# Imports Files
import config

# Importing the random module
import random

#
import time

from aiogram.utils import exceptions as tg_exceptions

# logs
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.token)
dp = Dispatcher(bot)

# ------------|| Create InlineKeyboard Button & MarkUp ||--------------
ToFavorite = InlineKeyboardMarkup(row_width=1)
button = InlineKeyboardButton("Save To Favorite",
                              callback_data='Save To Favorite')
ToFavorite.add(button)

# ---------------------------------------------------------------------
# ------------------|| Favorite songs for random ||--------------------
# ---------------------------------------------------------------------
favorite_song_for_random = [
    'holychords.pro/57', 'holychords.pro/1798', 'holychords.pro/807',
    'holychords.pro/8634', 'holychords.pro/111', 'holychords.pro/7063',
    'holychords.pro/31252', 'holychords.pro/748', 'holychords.pro/2319',
    'holychords.pro/278', 'holychords.pro/273', 'holychords.pro/4942',
    'holychords.pro/42851', 'holychords.pro/2339', 'holychords.pro/18615',
    'holychords.pro/40393', 'holychords.pro/24392', 'holychords.pro/3661',
    'holychords.pro/1325', 'holychords.pro/19624', 'holychords.pro/278',
    'holychords.pro/25006', 'holychords.pro/801', 'holychords.pro/7233',
    'holychords.pro/11052', 'holychords.pro/10891', 'holychords.pro/5380',
    'holychords.pro/1028', 'holychords.pro/3366', 'holychords.pro/11154',
    'holychords.pro/1078', 'holychords.pro/29055', 'holychords.pro/19624',
    'holychords.pro/10074', 'holychords.pro/18104', 'holychords.pro/28415',
    'holychords.pro/8732', 'holychords.pro/41264', 'holychords.pro/41258',
    'holychords.pro/4422', 'holychords.pro/2244', 'holychords.pro/31775',
    'holychords.pro/2017', 'holychords.pro/1798', 'holychords.pro/24095',
    'holychords.pro/2124', 'holychords.pro/6926', 'holychords.pro/7702',
    'holychords.pro/637', 'holychords.pro/818'
]

# --------------------------------------------------------------------
# ------------------|| Connect and Create DataBase ||-----------------
# --------------------------------------------------------------------
#
conn = sqlite3.connect('database.db')
c = conn.cursor()

#
c.execute(f'''
		CREATE TABLE IF NOT EXISTS users 
		(first_name TEXT, 
		last_name TEXT,
		username TEXT,
		chat_id INTEGER PRIMARY KEY,
		Date DATETIME DEFAULT (datetime('now')))
''')


# ---------------------------------------------------------------------
# --------------------------|| On Start Up ||--------------------------
# ---------------------------------------------------------------------
async def on_startup():
    me = await bot.me
    print(f'Username: @{me.username}\n'
          f'ID: {me.id}\n'
          f'↓↓↓ Start polling ↓↓↓')


# ---------------------------------------------------------------------
# ----------------------------|| /start ||-----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "Hello! This bot can help you search for songs on holychords.pro. \nTo get help, use the /help command."
    )
    await help(message)

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = "@" + message.from_user.username
    chat_id = message.chat.id

    # Check, if there is already chat_id in  Database
    c.execute('SELECT * FROM users WHERE chat_id=?', (chat_id,))
    user = c.fetchone()
    if user:
        # already in db
        pass
    else:
        # Saving to db
        date = "date"
        c.execute(f'INSERT INTO users (first_name, last_name, username, chat_id) VALUES (?, ?, ?, ?)',
                  (first_name, last_name, username, chat_id,))
        conn.commit()
    # saved to db


# | --------------------------------------------------------------------- |
# | --------------------------|| /identification ||---------------------- |
# | --------------------------------------------------------------------- |
@dp.message_handler(commands=["my_id", 'id', 'identification'])
async def user_id(message: types.Message):
    await message.reply(
        f"<b>Telegram ID</b>: {message.from_user.id}\n"
        f"<b>Chat ID</b>: {message.chat.id}\n"
        f"Other <b>message.from_user</b>:\n"
        f"{message.from_user}\n\n"
        f"Other <b>message</b>:\n"
        f"{message}",
        parse_mode=types.ParseMode.HTML)


# ---------------------------------------------------------------------
# --------------------------|| /favorite ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=["favorite", 'db'])
async def favorite(message: types.Message):
    # c.execute('SELECT * FROM users')
    # data = c.fetchall()
    # await message.answer(data)
    user_id = 'User_' + str(message.from_user.id)

    c.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{user_id}'")
    result = c.fetchone()

    c.execute(f'SELECT * FROM {user_id}')
    data = c.fetchall()

    if result is None or data == []:
        await message.reply("I don't have any record in 'Favorites' yet.")
    else:
        text = ''
        for index in range(len(data)):
            text += f'{index + 1}. {data[index][0]}\n'
        await message.reply(text)


# ---------------------------------------------------------------------
# ----------------------------|| /random ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=['random', 'r'])
async def random_song(message: types.Message):
    num_of_random_songs = message.text.split()
    max_num = len(favorite_song_for_random)

    if len(num_of_random_songs) == 1:
        await message.reply(
            "You can give me number of songs you wish to get\n/random {number of random song 🎧}\nhere is 3 song"
        )
        num_of_random_songs.append(3)

    elif re.search(r"\D", num_of_random_songs[1]):
        await message.reply(
            'After /random must go digit not a letter \n/random {number of random song 🎧}'
        )
        num_of_random_songs.pop(1)
        num_of_random_songs.append(0)

    elif int(num_of_random_songs[1]) == 0:
        await message.reply(
            "Here is 0 song\n/random {number of random song 🎧} \n*NUMBER NEEDS BE MORE THAN ZERO. Thanks 😊 "
        )

    if int(num_of_random_songs[1]) >= max_num:
        index_of_random_song = random.sample(range(0, max_num), max_num)
        await message.reply(f"I have only {max_num} saved random song")
        for i in range(len(index_of_random_song)):
            await message.answer(favorite_song_for_random[index_of_random_song[i]], reply_markup=ToFavorite)
            time.sleep(1 / 25)

    elif int(num_of_random_songs[1]) <= 30:
        index_of_random_song = random.sample(range(0, max_num),
                                             int(num_of_random_songs[1]))
        for i in range(len(index_of_random_song)):
            await message.answer(favorite_song_for_random[index_of_random_song[i]], reply_markup=ToFavorite)

    else:
        index_of_random_song = random.sample(range(0, max_num),
                                             int(num_of_random_songs[1]))
        for i in range(len(index_of_random_song)):
            await message.answer(favorite_song_for_random[index_of_random_song[i]], reply_markup=ToFavorite)
            time.sleep(1 / 25)


# ---------------------------------------------------------------------
# ----------------------------|| /new ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=['new', 'n'])
async def new_song(message: types.Message):
    num_of_songs = message.text.split()

    search_result = []

    if len(num_of_songs) == 1:
        await message.reply(
            "You can give me number of songs you wish to get\n/new {number of new song 🎧}\nhere is 3 song"
        )
        num_of_songs.append(3)

    elif re.search(r"\D", num_of_songs[1]):
        await message.reply(
            'After /new must go digit not a letter \n/new {number of new songs you wish to get 🎧}'
        )
        num_of_songs.pop(1)
        num_of_songs.append(0)

    elif int(num_of_songs[1]) == 0:
        await message.reply(
            "Here is 0 song\n/new {number of new song 🎧} \n*To get results number need to be more than zero. \nThanks 😊 "
        )

    if int(num_of_songs[1]) > 50:
        await message.reply("I am only able to handle 50 of new songs :(")
    else:
        # make url that are search for song
        url = "https://holychords.pro/musics?page=1"
        # print(url)

        # Make a request to https://holychords.pro/ with the search terms
        headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        #
        search_result = soup.find("div", id="entries").find(
            'div', class_="music_item media mt-3").find(
            'a', class_="mr-3 play").get("data-audio-id")

        link_list = []
        for id in range(int(search_result), int(search_result) - 400, -1):
            link_list.append("holychords.pro/" + str(id))

        print(len(link_list))

        index_of_random_song = random.sample(range(0, 400), int(num_of_songs[1]))

        for i in range(int(num_of_songs[1])):
            # {i+1}.
            await message.answer(f"{link_list[index_of_random_song[i]]}", reply_markup=ToFavorite)
            time.sleep(1 / 25)


# ---------------------------------------------------------------------
# ----------------------------|| /popular ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=['popular', 'top', 'chart', 'charts', 't'])
async def popular(message: types.Message):
    num_of_songs = message.text.split()

    search_result = []

    if len(num_of_songs) == 1:
        await message.reply(
            "You can give me number of songs you wish to get\n/top {number of top song 🎧}\nhere is 3 song"
        )
        num_of_songs.append(3)

    elif re.search(r"\D", num_of_songs[1]):
        await message.reply(
            'After /top must go digit not a letter \n/top {number of top songs you wish to get 🎧}'
        )
        num_of_songs.pop(1)
        num_of_songs.append(0)

    elif int(num_of_songs[1]) == 0:
        await message.reply(
            "Here is 0 song\n/top {number of top song 🎧} \n*To get results number need to be more than zero. \nThanks 😊 "
        )

    if int(num_of_songs[1]) > 100:
        await message.reply("I have only top 100 songs :(")
    else:
        # make url that are search for song
        url = "https://holychords.pro/charts"

        # Make a request to https://holychords.pro/ with the search terms
        headers = {
            "User-Agent":
                "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        for search_wrapper in soup.find_all("div",
                                            class_="media-body text-truncate"):
            for link in search_wrapper.find_all('a'):
                search_title = link.get_text()  # search_wrapper.get("a")["href"]
                search_url = link.get('href')
                search_result.append([search_url, search_title])

        for i in range(int(num_of_songs[1])):
            await message.answer(
                f'holychords.pro{search_result[i][0]}', reply_markup=ToFavorite)
            time.sleep(1 / 25)


# ---------------------------------------------------------------------
# --------------------------|| /help ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=["help", "info", "support"])
async def help(message: types.Message):
    help_text = "Here are the available commands:\n" \
                "/help - Show this help message\n" \
                "/search <song name> - Search for song on holychords.pro\n" \
                "/new <# of songs> - gives you new songs that were added to holychords.pro \n " \
                "/top <# of songs> - gives you top songs by holychords.pro \n " \
                "/random <# of songs> - gives you random songs from our playlist \n "
    await message.reply(help_text)


# ---------------------------------------------------------------------
# --------------------------|| /search ||----------------------------
# ---------------------------------------------------------------------
@dp.message_handler(commands=["search", 's'])
async def search(message: types.Message):
    # print("\n\n\n\n\n\n\n\n|--------------------| 🔦 New Search 🔍 |--------------------|")

    if message.text.startswith("/search"):
        # get the search prompt from message
        user_input = message.text[8:]
        song_name = user_input.split()
        search_prompt = ("+").join(song_name)
    else:
        # get the search prompt from message
        user_input = message.text[2:]
        song_name = user_input.split()
        search_prompt = ("+").join(song_name)

    if search_prompt == "":
        await message.reply("You forget include song name.\n"
                            "/search 'song name'")
    else:

        # make google url with search prompt/query and parameters to filter out everything except holycords
        url = f"https://www.google.com/search?q={str(search_prompt)}+site:holychords.pro"

        # make fake device, brouser verification to make site parse-able
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        # get the html code from website url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # find the url resultats
        search_results = []
        for search_wrapper in soup.find_all("div", class_="tF2Cxc"):
            search_url = search_wrapper.find("a")["href"]
            search_results.append(search_url)

        # Filter out links that aren't leads to song
        original_tuple = search_results
        required_tuple = tuple(
            filter(lambda x: re.match(r'^https://holychords\.pro/\d+$', x),
                   original_tuple))

        # Send separately link to song 3 times or less or doesn’t if 0 results
        for index in range(3 if len(required_tuple) >= 3 else len(required_tuple)):
            await message.answer(required_tuple[index][8:], reply_markup=ToFavorite)

        if len(required_tuple) == 0:
            # The text with a hyperlink
            text = 'Sorry, I couldn’t find, Try Google it 😞\n' \
                   'Google: <a href="google.com/search?q=' + str(search_prompt) + '">' + user_input + '</a>'

            # Send the message with the hyperlink
            await message.reply(text=text, parse_mode=types.ParseMode.HTML)


# ---------------------------------------------------------------------
# -------------------------|| CallbackQuery ||-------------------------
# ---------------------------------------------------------------------
@dp.callback_query_handler()
async def process_callback_click(callback_query: types.CallbackQuery):
    Save_to_me_button = InlineKeyboardButton(text='Me', callback_data='Save_to_me')
    Save_to_group_button = InlineKeyboardButton(text='Group',
                                                callback_data='Save_to_group')
    Saved_button = InlineKeyboardButton(text='Saved', callback_data='Saved')

    where_to_safe = InlineKeyboardMarkup(
        inline_keyboard=[[Save_to_me_button, Save_to_group_button]])

    saved_markup = InlineKeyboardMarkup(
        inline_keyboard=[[Saved_button]])

    # Check where button "Save To Favorite" where clicked and if in group give option to save group playlist
    if callback_query.data == 'Save To Favorite':

        try:
            if callback_query.message.chat.type == "group":
                await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                    callback_query.message.message_id,
                                                    reply_markup=where_to_safe)
            else:
                chat_id = 'Chat_' + str(callback_query.message.chat.id).replace('-', '_')
                user_id = 'User_' + str(callback_query.from_user.id)

                c.execute(f'''CREATE TABLE IF NOT EXISTS {user_id}
				               (Song TEXT PRIMARY KEY UNIQUE,
				                Chat_id TEXT,
												User_id TEXT,
				                Date DATETIME DEFAULT (datetime('now')))
				            ''')

                Song = str(callback_query.message.text)
                # Check, if there is this song in database
                c.execute(f'SELECT * FROM {user_id} WHERE Song=?', (Song,))
                user = c.fetchone()
                if user:
                    # Song already in 'Favorite'
                    await bot.send_message(callback_query.message.chat.id,
                                           "This song already in 'Favorite'")
                    await bot.answer_callback_query(callback_query.id)

                else:
                    # in process to add song to 'Favorite'
                    c.execute(
                        f'INSERT INTO {user_id} (Song, Chat_id, User_id) VALUES (?, ?, ?)', (Song, chat_id, user_id,))

                    conn.commit()

                    # added song to 'Favorite'

                    await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                        callback_query.message.message_id,
                                                        reply_markup=saved_markup)
                    await bot.answer_callback_query(callback_query.id)

        except tg_exceptions.MessageNotModified:
            # This exception is raised if the message is already edited with the same reply markup
            print('happend again')
            pass





    elif callback_query.data == "Save_to_group":
        chat_id = 'Chat_' + str(callback_query.message.chat.id).replace('-', '_')
        user_id = 'User_' + str(callback_query.from_user.id)

        c.execute(f'''CREATE TABLE IF NOT EXISTS {chat_id}
		               (Song TEXT PRIMARY KEY UNIQUE,
		                Chat_id TEXT,
										User_id TEXT,
		                Date DATETIME DEFAULT (datetime('now')))
		            ''')

        Song = str(callback_query.message.text)
        # Check, if there is this song in database
        c.execute(f'SELECT * FROM {chat_id} WHERE Song=?', (Song,))
        user = c.fetchone()
        if user:
            # Song already in 'Favorite'
            await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                callback_query.message.message_id,
                                                reply_markup=saved_markup)
            await bot.send_message(callback_query.message.chat.id,
                                   "This song already in 'Favorite'")
            await bot.answer_callback_query(callback_query.id)

        else:
            # in process to add song to 'Favorite'
            c.execute(
                f'INSERT INTO {chat_id} (Song, Chat_id, User_id) VALUES (?, ?, ?)', (
                    Song,
                    chat_id,
                    user_id,
                ))

            conn.commit()

            await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                callback_query.message.message_id,
                                                reply_markup=saved_markup)
            # added song to 'Favorite'
            await bot.answer_callback_query(callback_query.id)




    elif callback_query.data == "Save_to_me":
        chat_id = 'Chat_' + str(callback_query.message.chat.id).replace('-', '_')
        user_id = 'User_' + str(callback_query.from_user.id)

        c.execute(f'''CREATE TABLE IF NOT EXISTS {user_id}
		               (Song TEXT PRIMARY KEY UNIQUE,
		                Chat_id TEXT,
										User_id TEXT,
		                Date DATETIME DEFAULT (datetime('now')))
		            ''')

        Song = str(callback_query.message.text)
        # Check, if there is this song in database
        c.execute(f'SELECT * FROM {user_id} WHERE Song=?', (Song,))
        user = c.fetchone()
        if user:
            # Song already in 'Favorite'
            await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                callback_query.message.message_id,
                                                reply_markup=saved_markup)
            await bot.send_message(callback_query.message.chat.id,
                                   "This song already in 'Favorite'")
            await bot.answer_callback_query(callback_query.id)

        else:
            # in process to add song to 'Favorite'
            c.execute(
                f'INSERT INTO {user_id} (Song, Chat_id, User_id) VALUES (?, ?, ?)', (
                    Song,
                    chat_id,
                    user_id,
                ))

            conn.commit()
            await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                                callback_query.message.message_id,
                                                reply_markup=saved_markup)
            # added song to 'Favorite'
            await bot.answer_callback_query(callback_query.id)

    else:
        print(callback_query.data)
        await bot.answer_callback_query(callback_query.id)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)

# Close connection with database
conn.close()
