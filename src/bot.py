from typing import Final
from os import getenv
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,ContextTypes
import aiohttp
from dotenv import load_dotenv,find_dotenv

print('Starting up bot...')

load_dotenv(find_dotenv())

# Telegram Bot
BOT_USERNAME: Final = getenv("BOT_USERNAME")
BOT_API: Final = getenv("BOT_API")

#OMDB
OMDB: Final = "http://www.omdbapi.com"
OMDB_API: Final = getenv("OMDB_API") 

#TMDB
TMDB_API: Final = getenv("TMDB_API")

#IMDB
IMDB_LINK: Final = "https://www.imdb.com/title/"


class Botz:
    
    INTRO_MSG = "Heyy I\'m Sarah , Maintained by @akkupy \n" \
                "Type in /find <movie-name> to get the Movie Details \n" 

    def __init__(self) -> None:
        self.app = Application.builder().token(BOT_API).build()

        # Set up bot memory
        self.memory: list = []

        # Set up bot movie file cache memory
        self.movie_memory:list = []

    # /start command
    async def start_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_chat_action(action="typing")
        await update.message.reply_photo(photo="https://raw.githubusercontent.com/AkkuPY/Sara-Bot/main/Assets/Sara_Bot.jpg",caption=self.INTRO_MSG)

    # Replying to text other than commands
    async def any_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message_type: str = update.message.chat.type
        if message_type not in ['group','supergroup']:
            await update.message.reply_text(f"Unknown command: {update.message.text} -> To Search Movie use : /find <movie_name>")

    # Error Handling
    async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(f'Update {update} caused error {context.error}')
        await update.message.reply_text("Sorry, this movie/show is unknown to me")


    # /find command
    async def find_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE ) -> None:
        if len(self.memory) == 25:
            self.memory = []
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
            data_str =  f"🎬 Title:    {movie_data['Title']} ({movie_data['Year']})\n\n" \
                        f"📖 Genre:    {movie_data['Genre']}\n\n" \
                        f"⭐ Rating:    {movie_data['imdbRating']}/10\n\n" \
                        f"🕤 Runtime:    {movie_data['Runtime']}\n\n" \
                        f"🎭 Actors:    {movie_data['Actors']}\n\n" \
                        f"🧑 Director:    {movie_data['Director']}\n\n" \
                        f"🆔 IMDB ID:    {movie_data['imdbID']}\n\n"
            
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
                        else:
                            Poster = data['tv_results'][0]['backdrop_path']

                URL = str(TMDB_IMAGE_BASE+Poster)
                await update.message.reply_photo(photo=URL)


            buttons = [
                [InlineKeyboardButton("Plot", callback_data=f"{movie_data['Title']}:plot"),
                InlineKeyboardButton("Ratings", callback_data=f"{movie_data['Title']}:ratings")],
                [InlineKeyboardButton("Awards", callback_data=f"{movie_data['Title']}:awards"),
                InlineKeyboardButton("Languages", callback_data=f"{movie_data['Title']}:languages"),
                InlineKeyboardButton("Rated", callback_data=f"{movie_data['Title']}:rated")],
                [InlineKeyboardButton("IMDB page", url=f"{IMDB_LINK}{movie_data['imdbID']}"),
                InlineKeyboardButton("Trailer", url=await self.get_trailer_url(movie_data["imdbID"],movie_data['Title']))],
            ]
            await update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons))

            Flag = False
            for item in self.movie_memory:
                if movie_data['imdbID'] == item["imdb_id"]:
                    file_data = item
                    break

            else:
                Flag = True

            if not Flag:
                from_chat_id,message_id = file_data['from_chat_id'],file_data['message_id']

                to_chat_id = update.message.chat.id

                await update.message._bot.forward_message(to_chat_id,from_chat_id,message_id)
        else:
            await update.message.reply_text("Movie Not Found! Check the spelling.")

        
            

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
        return f"{movie_json['Title']} ratings:\n{rating_str}"

    @staticmethod
    def get_rated(movie_json: dict) -> str:
        return f"{movie_json['Title']} rated:\n{movie_json['Rated']}"


    @staticmethod
    def get_plot(movie_json: dict) -> str:
        return f"{movie_json['Title']} plot:\n{movie_json['Plot']}"


    @staticmethod
    def get_languages(movie_json: dict) -> str:
        return f"{movie_json['Title']} languages:\n{movie_json['Language']}"


    @staticmethod
    def get_awards(movie_json: dict) -> str:
        return f"{movie_json['Title']} awards:\n{movie_json['Awards']}"

    # Query Handler
    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query.data
        await update.callback_query.answer()

        title, kword = query.split(":")
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
            await update.callback_query.message.reply_text(self.get_rating(data))
        elif kword == "plot":
            await update.callback_query.message.reply_text(self.get_plot(data))
        elif kword == "rated":
            await update.callback_query.message.reply_text(self.get_rated(data))
        elif kword == "awards":
            await update.callback_query.message.reply_text(self.get_awards(data))
        elif kword == "languages":
            await update.callback_query.message.reply_text(self.get_languages(data))


    async def movie_saver(self,update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:

        imdb_id = "".join(context.args)

        if imdb_id == "":
            await update.message.reply_text('Enter the Movie/Series IMDB id along with /save. Go to /help for more details.')


        elif update.message.reply_to_message == None: 
            await update.message.reply_text('Use this command as a reply to the file to be saved. Go to /help for more details.')
        else:
            message_id = update.message.reply_to_message.id

            from_chat_id = update.message.chat.id

            self.movie_memory.append({
                'imdb_id' : imdb_id,
                'from_chat_id' : from_chat_id,
                'message_id' : message_id,
            })

            await update.message.reply_text('Movie/Series saved on database. ')

    async def movie_remover(self,update: Update,context: ContextTypes.DEFAULT_TYPE) -> None:

        imdb_id = "".join(context.args)

        if imdb_id == "":
            await update.message.reply_text('Enter the Movie/Series IMDB id along with /remove. Go to /help for more details.')

        else:
            count = 0
            for item in self.movie_memory:
                count+=1
                if imdb_id == item["imdb_id"]:
                    del self.movie_memory[count-1]
                    await update.message.reply_text('Movie/Series removed from database.')
                    break

            else:
                await update.message.reply_text('Movie/Series not found on database.')
            