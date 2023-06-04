from typing import Final
from os import getenv
from telegram import Update,InputMediaPhoto,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,ContextTypes

import aiohttp

from dotenv import load_dotenv,find_dotenv

print('Starting up bot...')

load_dotenv(find_dotenv())

BOT_USERNAME: Final = getenv("BOT_USERNAME")
BOT_API: Final = getenv("BOT_API")

OMDB: Final = "http://www.omdbapi.com"
OMDB_API: Final = getenv("OMDB_API") 


class Bot:
    # HELP_MSG = "Available commands:\n\n" \
    #            "    /find [title] [y=year] (/find The Godfather y=1972)\n\n\n" \
    #            "After you find a movie, use buttons under it to get more information or " \
    #            "use commands to get information about last movie from bot memory:\n\n" \
    #            "    /rate|/rated -- movie PG\n" \
    #            "    /award|/awards -- awards and nominations\n" \
    #            "    /rating|/ratings -- movie ratings\n" \
    #            "    /language|/languages -- movie languages\n" \
    #            "    /plot -- short plot description\n" \
    #            "    /link - IMDB movie page\n"
    
    INTRO_MSG = "Heyy I\'m Sarah , Maintained by @akkupy \n" \
                "Type in /m <movie-name> to get the Movie Details \n" 

    def __init__(self) -> None:
        self.app = Application.builder().token(BOT_API).build()

        # Set up bot memory
        self.memory: list = []

    async def start_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_chat_action(action="typing")
        await update.message.reply_photo(photo="https://raw.githubusercontent.com/AkkuPY/Sara-Bot/main/Assets/Sara_Bot.jpg",caption=self.INTRO_MSG)


    # async def help_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     await update.message.reply_text(self.HELP_MSG)

    async def any_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Bot response on not coded text"""
        await update.message.reply_text(f"Unknown command: {update.message.text} -> /help")

    async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(f'Update {update} caused error {context.error}')
        await update.message.reply_text("Sorry, this movie/show is unknown to me")

    # def handle_response(text: str) -> str:
    #     processed: str = text.lower()

    #     if 'hello' in processed:
    #         return 'Hey there!'

    #     if 'how are you' in processed:
    #         return 'I\'m good!'

    #     if 'i love python' in processed:
    #         return 'Remember to subscribe!'

    #     return 'I don\'t understand'


    # async def handle_message(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     message_type: str = update.message.chat.type
    #     text: str = update.message.text

    #     print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    #     if message_type == 'group':
    #         if BOT_USERNAME in text:
    #             new_text: str = text.replace(BOT_USERNAME, '').strip()
    #             response: str = self.handle_response(new_text)
    #         else:
    #             return  
    #     else:
    #         response: str = self.handle_response(text)

    #     print('Bot:', response)
    #     await update.message.reply_text(response)


    @staticmethod
    async def empty_memory(update: Update) -> None:
        await update.message.reply_text("My memory is empty😕.\nLook something up! -> /find")

    async def find_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE ) -> None:
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
        async with aiohttp.ClientSession() as session:
            async with session.get(OMDB, params = omdb_params) as response:
                movie_data = await response.json()
                self.memory.append(movie_data)
                if movie_data["Response"] != "False":                      
                    data_str = f"Title:    {movie_data['Title']} ({movie_data['Year']})\n" \
                            f"Genre:    {movie_data['Genre']}\n" \
                            f"Rating:    {movie_data['imdbRating']}/10\n" \
                            f"Runtime:    {movie_data['Runtime']}\n" \
                            f"Actors:    {movie_data['Actors']}\n" \
                            f"Director:    {movie_data['Director']}\n"
                    async with session.get(movie_data["Poster"]) as poster:
                        await update.message.reply_photo(photo=str(poster.url))

                    buttons = [
                    [InlineKeyboardButton("Plot", callback_data=f"{movie_data['Title']}:plot"),
                    #InlineKeyboardButton("Trailer", url=self.get_trailer_url(movie_data["imdbID"])),
                    InlineKeyboardButton("Ratings", callback_data=f"{movie_data['Title']}:ratings"),
                    InlineKeyboardButton("Awards", callback_data=f"{movie_data['Title']}:awards"),
                    InlineKeyboardButton("Languages", callback_data=f"{movie_data['Title']}:languages"),
                    InlineKeyboardButton("Rated", callback_data=f"{movie_data['Title']}:rated")],
                    #[InlineKeyboardButton("IMDB page", url=f"{IMDB_LINK}{movie_data['imdbID']}")],
                    ]
                    await update.message.reply_text(data_str, reply_markup=InlineKeyboardMarkup(buttons))
                else:
                    await update.message.reply_text("Movie Not Found! Check the spelling.")
            

    # @staticmethod
    # def get_trailer_url(imdb_id: str) -> str:
    #     """Return movie youtube trailer url as string
    #     using IMDB API
    #     """
    #     imdb_params = {
    #         "apiKey": IMDB_API,
    #         "id": imdb_id
    #     }
    #     return requests.get(IMDB_TRAILER_REQ, imdb_params).json()["videoUrl"]

    # @property
    # def get_link(self) -> str:
    #     """Imdb movie link getter"""
    #     return f"{self.memory['Title']} on IMDB:\n{IMDB_LINK}{self.memory['imdbID']}"

    # def link(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     """/link command

    #     Print out IMDB link of the movie in memory
    #     """
    #     self.logger.info("/link called")
    #     if self.memory:
    #         update.message.reply_text(self.get_link)
    #     else:
    #         self.empty_memory(update)

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


    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query.data
        await update.callback_query.answer()

        title, kword = query.split(":")
        for item in self.memory:
            if title == item["Title"]:
                data = item
                print("Using Cached Data.")
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
                    print("Using API data.")
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
