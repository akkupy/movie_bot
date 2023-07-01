from typing import Final
from os import getenv,execl
import sys
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,ContextTypes
import aiohttp
from dotenv import load_dotenv,find_dotenv
import mysql.connector as msc
import time
from tcp_latency import measure_latency

print('Starting up bot...')

load_dotenv(find_dotenv())

# Telegram Bot
BOT_USERNAME: Final = getenv("BOT_USERNAME")
BOT_API: Final = getenv("BOT_API")

#OMDB
OMDB: Final = "http://www.omdbapi.com"
OMDB_SITE: Final = "www.omdbapi.com"
OMDB_API: Final = getenv("OMDB_API") 

#TMDB
TMDB_API: Final = getenv("TMDB_API")
TMDB_SITE: Final = "api.themoviedb.org"

#IMDB
IMDB_LINK: Final = "https://www.imdb.com/title/"

#MySQL
MYSQL_HOST: Final = getenv("MYSQL_HOST")
MYSQL_PORT: Final = 3306
MYSQL_USER: Final = getenv("MYSQL_USER")
MYSQL_PASSWORD: Final = getenv("MYSQL_PASSWORD")
MYSQL_DATABASE: Final = getenv("MYSQL_DATABASE")
CREATE_TABLE: Final = getenv("CREATE_TABLE",True)


class Botz:
    
    INTRO_MSG = "*Heyy I\'m Sara , A Movie Bot \n" \
                "Type in /help for the list of available commands* \n" 
    
    HELP_MSG = "*AVAILABLE COMMANDS*\n\n" \
               " * Command :* /start\n" \
               " * Description :* Gives the intro.\n\n" \
               " * Command :* /help\n" \
               " * Description :* Lists the available commands.\n\n" \
               " * Command :* /status\n" \
               " * Description :* Returns the status of the bot.\n\n" \
               " * Command :* /find movie-name \n" \
               " * Description :* " \
               " Gives the details of the movie/tvshow specified." \
               " Enter the movie name as argument of /find command." \
               " Use buttons under it to get more information. \n" \
               " eg: /find The Godfather \n\n" \
               " * Command :* /find movie-name y=year\n" \
               " * Description :* " \
               " Gives the details of the movie/tvshow specified." \
               " Enter the movie name and year as argument of /find command." \
               " Use buttons under it to get more information. \n" \
               " eg: /find The Godfather y=1972\n\n" \
               " * Command :* /save IMDB-id \n" \
               " * Description :* " \
               " Enter the imdb id of the movie/tvshow as argument." \
               " Use /find command to find the IMDB id for a movie/tv show." \
               " Saves the replied message/file in the database with the given imdb id." \
               " Always use this command as a reply to the file to be saved.\n " \
               " eg: /save tt1477834\n\n" \
               " * Command :* /remove IMDB-id \n" \
               " * Description :* " \
               " Enter the imdb id of the movie/tvshow as argument." \
               " Use /find command to find the IMDB id for a movie/tv show." \
               " Removes the file of the specified imdb id from the database.\n" \
               " eg: /remove tt1477834\n\n" \
               " * Command :* /list \n" \
               " * Description :* Returns the number of movies/series currently indexed on database.\n" \
               
    MOVIE_NOT_FOUND_MSG = "*{} is not currently Indexed on my database. 😔*\n\n" \
                "If you have this movie on your chat or in other groups , \n" \
                "    - Forward that movie into my chat or into this group and ,  \n" \
                "    - Use '*/save {}*' as a reply to that movie file to save the movie on my database. \n" 
    
    REBOOT_WAIT_MESSAGE = "Rebooting Sara. Please wait ⏲️" 

    REBOOT_SUCCESS_MESSAGE = "Sara is Back 😃"

    STATUS_MESSAGE = "*Sara is Alive.* 😃 \n\n" \
                "*Database Status :* {} \n" \
                "*Database Latency :* {} \n" \
                "*Movies Available :* {} \n\n" \
                "*OMDB :* {} \n" \
                "*OMDB Latency :* {} \n\n" \
                "*TMDB :* {} \n" \
                "*TMDB Latency :* {} \n" 

    MOVIE_NOT_FOUND = "*Movie/Series NOT FOUND. \n" \
                "Check the spelling.* \n"

    FIND_MSG = "*Enter the Movie/Series NAME along with /find. \n" \
            "Go to /help for more details.* \n"  
    
    INVALID_FIND_MSG = "*Unknown command : {}* \n" \
            "*To Search Movie use : /find <movie_name>* \n"

    SAVE_MSG = "*Enter the Movie/Series IMDB ID along with /save. \n" \
            "Go to /help for more details.* \n"
    
    SAVE_REPLY_MSG = "*Use this command as a reply to the file to be saved. \n" \
            "Go to /help for more details.* \n"
    
    REMOVE_MSG = "*Enter the Movie/Series IMDB ID along with /remove. \n" \
            "Go to /help for more details.* \n"
    
    CHECK_STATUS_MSG = "Gathering data. Please wait ⏲️"  

    def __init__(self) -> None:
        self.app = Application.builder().token(BOT_API).build()

        # Set up bot memory
        self.memory: list = []

        # Set up bot movie file cache memory
        self.movie_memory:list = []

        # Set up Mysql Database
        self.connection = msc.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        self.cursor = self.connection.cursor()
        if CREATE_TABLE == 'True':
            self.cursor.execute("Create table movie_data(imdb_id varchar(20),from_chat_id varchar(20),message_id varchar(20))")

    async def reboot(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  
        msg = await update.message.reply_text(self.REBOOT_WAIT_MESSAGE)
        time.sleep(5)
        await msg.edit_text(self.REBOOT_SUCCESS_MESSAGE)
        execl(sys.executable, f'"{sys.executable}"', *sys.argv)

    async def status(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = await update.message.reply_text(self.CHECK_STATUS_MSG) 
        if self.connection.is_connected():
            db_status = "Connected ✅"
            db_latency = str(round(measure_latency(host=MYSQL_HOST, port=MYSQL_PORT, timeout=2.5)[0])) + "ms ⏱️"
            self.cursor.execute("select count(*) from movie_data")
            movie_number = str(self.cursor.fetchone()[0]) + ' 🎬'
        else:
            db_status = "Disconnected ❌" 
            db_latency = "N/A ❌"
            movie_number = "N/A ❌"

        omdb_params = {
            "apikey": OMDB_API,
            "t": '2012',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(OMDB, params = omdb_params) as response:
                movie_data = await response.json()
                if movie_data["Response"] != "False":
                    omdb_status = "API Available.✅"
                    omdb_latency = str(round(measure_latency(host=OMDB_SITE, timeout=2.5)[0])) + "ms ⏱️"

                    find_TMDB = f'https://api.themoviedb.org/3/find/{movie_data["imdbID"]}?api_key={TMDB_API}&external_source=imdb_id'

                    async with aiohttp.ClientSession() as session:
                        async with session.get(find_TMDB) as response:
                            data = await response.json()
                            if 'success' not in data.keys():
                                tmdb_status = "API Available ✅"
                                tmdb_latency = str(round(measure_latency(host=TMDB_SITE, timeout=2.5)[0])) + "ms ⏱️"
                            else:
                                tmdb_status = "API Unavailable ❌"
                                tmdb_latency = "N/A ❌"
                           
                else:
                    omdb_status = "API Unavailable.❌"
                    omdb_latency = "N/A ❌"
                    tmdb_status = "API Unavailable.❌"
                    tmdb_latency = "N/A ❌"
        
        await message.edit_text(self.STATUS_MESSAGE.format(db_status,db_latency,movie_number,omdb_status,omdb_latency,tmdb_status,tmdb_latency),parse_mode='markdown')
        


    # /start command
    async def start_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_chat_action(action="typing")
        await update.message.reply_photo(photo="https://raw.githubusercontent.com/AkkuPY/Sara-Bot/main/Assets/Sara_Bot.jpg",caption=self.INTRO_MSG,parse_mode='markdown')

    # /help command
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(self.HELP_MSG,parse_mode='markdown')

    # Replying to text other than commands
    async def any_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message_type: str = update.message.chat.type
        if message_type not in ['group','supergroup']:
            await update.message.reply_text(self.INVALID_FIND_MSG.format(update.message.text),parse_mode='markdown')

    # Error Handling
    async def error(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(f'\nUpdate\n{update.message}\n\ncaused error {context.error}')
        await update.message.reply_text("*Sorry, Sara encountered an error.*",parse_mode='markdown')


    # /find command
    async def find_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE ) -> None:
        if len(self.memory) == 25:
            self.memory = []
        if len(self.movie_memory) == 25:
            self.movie_memory = []

        if "".join(context.args) == "":
            await update.message.reply_text(self.FIND_MSG,parse_mode='markdown')

        else:
            if "y=" in context.args[-1]:               
                movie_name = " ".join(context.args[:-1])
                omdb_params = {
                    "apikey": OMDB_API,
                    "t": movie_name,
                    "y": context.args[-1][2:]
                }
            else:
                movie_name = " ".join(context.args)
                omdb_params = {
                    "apikey": OMDB_API,
                    "t": movie_name,
                }
            
            for item in self.memory:
                if movie_name == item["Title"].lower() or movie_name == item['Title']:
                    movie_data = item
                    break
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(OMDB, params = omdb_params) as response:
                        movie_data = await response.json()
                        if movie_data["Response"] != "False": 
                            self.memory.append(movie_data)  
            

            if movie_data["Response"] != "False":                    
                data_str =  f"🎬 *Title:*    {movie_data['Title']} ({movie_data['Year']})\n\n" \
                            f"📖 *Genre:*    {movie_data['Genre']}\n\n" \
                            f"⭐ *Rating:*    {movie_data['imdbRating']}/10\n\n" \
                            f"🕤 *Runtime:*    {movie_data['Runtime']}\n\n" \
                            f"🎭 *Actors:*    {movie_data['Actors']}\n\n" \
                            f"🧑 *Director:*    {movie_data['Director']}\n\n" \
                            f"🆔 *IMDB ID:*    {movie_data['imdbID']}\n\n"
                
                if movie_data['Poster'] != 'N/A':
                    await update.message.reply_photo(photo=movie_data['Poster'])
                else:
                    find_TMDB = f'https://api.themoviedb.org/3/find/{movie_data["imdbID"]}?api_key={TMDB_API}&external_source=imdb_id'

                    TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/original'

                    async with aiohttp.ClientSession() as session:
                        async with session.get(find_TMDB) as response:
                            data = await response.json()
                            if data['movie_results'] != []:
                                Poster = data['movie_results'][0]['backdrop_path']
                                URL = str(TMDB_IMAGE_BASE+Poster)
                                await update.message.reply_photo(photo=URL)
                            elif data['tv_results'] != []:
                                Poster = data['tv_results'][0]['backdrop_path']
                                URL = str(TMDB_IMAGE_BASE+Poster)
                                await update.message.reply_photo(photo=URL)
                        
                buttons = [
                    [InlineKeyboardButton("Plot", callback_data=f"{movie_data['Title']};plot"),
                    InlineKeyboardButton("Ratings", callback_data=f"{movie_data['Title']};ratings")],
                    [InlineKeyboardButton("Awards", callback_data=f"{movie_data['Title']};awards"),
                    InlineKeyboardButton("Languages", callback_data=f"{movie_data['Title']};languages"),
                    InlineKeyboardButton("Rated", callback_data=f"{movie_data['Title']};rated")],
                    [InlineKeyboardButton("IMDB page", url=f"{IMDB_LINK}{movie_data['imdbID']}"),
                    InlineKeyboardButton("Trailer", url=await self.get_trailer_url(movie_data["imdbID"],movie_data['Title']))],
                    [InlineKeyboardButton("Get Movie", callback_data=f"{movie_data['Title']};getmovie")]
                ]
                await update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons),parse_mode='markdown')

            else:
                await update.message.reply_chat_action(action="typing")
                await update.message.reply_photo(photo='https://raw.githubusercontent.com/akkupy/movie_bot/main/assets/check_spelling.jpg',caption=self.MOVIE_NOT_FOUND,parse_mode='markdown')

        
            

    @staticmethod
    async def get_trailer_url(imdb_id: str,Title: str) -> None:

        find_TMDB = f'https://api.themoviedb.org/3/find/{imdb_id}?api_key={TMDB_API}&external_source=imdb_id'

        YOUTUBE_BASE_URL = 'https://www.youtube.com/watch?v='

        async with aiohttp.ClientSession() as session:
            async with session.get(find_TMDB) as response:
                data = await response.json()
                if data['movie_results'] != []:
                    TMDB_ID = data['movie_results'][0]['id']
                    TYPE = 'movie'
                elif data['tv_results'] != []:
                    TMDB_ID = data['tv_results'][0]['id']
                    TYPE = 'tv'
                else:
                    return f'https://www.youtube.com/results?search_query={Title}'

            video_TMDB = f'https://api.themoviedb.org/3/{TYPE}/{TMDB_ID}/videos?api_key={TMDB_API}'
            async with session.get(video_TMDB) as response:
                data = await response.json()
                if data['results'] != []:
                    video = data['results'][0]['key']
                else:
                    return f'https://www.youtube.com/results?search_query={Title}'
            return YOUTUBE_BASE_URL+video


    @staticmethod
    def get_rating(movie_json: dict) -> str:
        rating_str: str = ""
        for rating in movie_json["Ratings"]:
            rating_str += f"{rating['Source']}: {rating['Value']}\n"
        return f"*{movie_json['Title']} Ratings* ⭐\n\n{rating_str}"

    @staticmethod
    def get_rated(movie_json: dict) -> str:
        return f"*{movie_json['Title']} Rated* 🔞\n\n{movie_json['Rated']}"


    @staticmethod
    def get_plot(movie_json: dict) -> str:
        return f"*{movie_json['Title']} Plot* 📖\n\n{movie_json['Plot']}"


    @staticmethod
    def get_languages(movie_json: dict) -> str:
        return f"*{movie_json['Title']} Languages* 🗣️\n\n{movie_json['Language']}"


    @staticmethod
    def get_awards(movie_json: dict) -> str:
        return f"*{movie_json['Title']} Awards* 🏆\n\n{movie_json['Awards']}"
    

    @staticmethod
    def get_movie(self,movie_json: dict) -> str:
        Flag = False
        for item in self.movie_memory:
            if movie_json['imdbID'] == item["imdb_id"]:
                file_data = item
                break

        else:
            self.cursor.execute("select count(*) from movie_data where imdb_id = '{}'".format(movie_json['imdbID']))
            if self.cursor.fetchone()[0] != 0:
                self.cursor.execute("select * from movie_data where imdb_id = '{}'".format(movie_json['imdbID']))
                data = self.cursor.fetchone()
                file_data = {
                    'imdb_id' : data[0],
                    'from_chat_id' : data[1],
                    'message_id' : data[2],
                }
                self.movie_memory.append({
                    'imdb_id' : data[0],
                    'from_chat_id' : data[1],
                    'message_id' : data[2],
                })
            else:
                Flag = True
                from_chat_id = message_id = None
                return from_chat_id,message_id
                    
        if not Flag:
            from_chat_id,message_id = file_data['from_chat_id'],file_data['message_id']
            return from_chat_id,message_id

        

    # Query Handler
    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query.data
        await update.callback_query.answer()

        title, kword = query.split(";")
        for item in self.memory:
            if title == item["Title"]:
                data = item
                break
        else:
            omdb_params = {
                "apikey": OMDB_API,
                "t": title,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(OMDB, params=omdb_params) as result:
                    data = await result.json()
                    self.memory.append(data)
        if kword == "ratings":
            await update.callback_query.message.reply_text(self.get_rating(data),parse_mode='markdown')
        elif kword == "plot":
            await update.callback_query.message.reply_text(self.get_plot(data),parse_mode='markdown')
        elif kword == "rated":
            await update.callback_query.message.reply_text(self.get_rated(data),parse_mode='markdown')
        elif kword == "awards":
            await update.callback_query.message.reply_text(self.get_awards(data),parse_mode='markdown')
        elif kword == "languages":
            await update.callback_query.message.reply_text(self.get_languages(data),parse_mode='markdown')
        elif kword == "getmovie":
            from_chat_id,message_id = self.get_movie(self,data)
            if from_chat_id == None:
                await update.callback_query.message.reply_text(self.MOVIE_NOT_FOUND_MSG.format(data['Title'],data["imdbID"]),parse_mode='markdown')
            else:
                await update.callback_query.message._bot.forward_message(update.callback_query.message.chat.id,from_chat_id,message_id)


    async def movie_saver(self,update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:                                                                                                                                                                                                       

        imdb_id = "".join(context.args)

        if imdb_id == "":
            await update.message.reply_text(self.SAVE_MSG,parse_mode='markdown')


        elif update.message.reply_to_message == None: 
            await update.message.reply_text(self.SAVE_REPLY_MSG,parse_mode='markdown')
        else:
            message_id = update.message.reply_to_message.id

            from_chat_id = update.message.chat.id

            self.cursor.execute("select count(*) from movie_data where imdb_id = '{}'".format(imdb_id))
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("insert into movie_data values('{}',{},{})".format(imdb_id,from_chat_id,message_id))
                self.connection.commit()
                await update.message.reply_text('*Movie/Series saved on database.*\n',parse_mode='markdown')
            else:
                await update.message.reply_text('*Movie/Series already present on database.*\n',parse_mode='markdown')

    async def movie_remover(self,update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:

        imdb_id = "".join(context.args)

        if imdb_id == "":
            await update.message.reply_text(self.REMOVE_MSG,parse_mode='markdown')

        else:

            self.cursor.execute("select count(*) from movie_data where imdb_id = '{}'".format(imdb_id))
            if self.cursor.fetchone()[0] != 0:
                self.cursor.execute("delete from movie_data where imdb_id = '{}'".format(imdb_id))
                self.connection.commit()
                await update.message.reply_text('*Movie/Series deleted from database.*\n',parse_mode='markdown')
            else:
                await update.message.reply_text('*Movie/Series not found on database.*\n',parse_mode='markdown')

            count = 0
            for item in self.movie_memory:
                if imdb_id == item["imdb_id"]:
                    del self.movie_memory[count]
                count+=1

    async def movie_list(self,update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:

        self.cursor.execute("select count(*) from movie_data")
        number = self.cursor.fetchone()[0]
        await update.message.reply_text(f'*{number} Movies/Series 🎬 found on database.*',parse_mode='markdown')
            
