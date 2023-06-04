from typing import Final
from os import getenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes,Updater
import asyncio

from dotenv import load_dotenv,find_dotenv

print('Starting up bot...')

load_dotenv(find_dotenv())

BOT_USERNAME: Final = getenv("BOT_USERNAME")
BOT_API: Final = getenv("BOT_API")

OMDB: Final = "http://www.omdbapi.com"
OMDB_API: Final = getenv("OMDB_API") 


class Bot:
    HELP_MSG = "Available commands:\n\n" \
               "    /find [title] [y=year] (/find The Godfather y=1972)\n\n\n" \
               "After you find a movie, use buttons under it to get more information or " \
               "use commands to get information about last movie from bot memory:\n\n" \
               "    /rate|/rated -- movie PG\n" \
               "    /award|/awards -- awards and nominations\n" \
               "    /rating|/ratings -- movie ratings\n" \
               "    /language|/languages -- movie languages\n" \
               "    /plot -- short plot description\n" \
               "    /link - IMDB movie page\n"
    
    INTRO_MSG = "Heyy I\'m Sarah , Maintained by @akkupy \n" \
                "Type in /help to get the available commands \n" 

    def __init__(self) -> None:
        self.app = Application.builder().token(BOT_API).build()

        # Set up bot memory
        self.memory: dict = {} 

    async def start_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_chat_action(action="typing")
        await update.message.reply_photo(photo="https://raw.githubusercontent.com/AkkuPY/Sara-Bot/main/Assets/Sara_Bot.jpg",caption=self.INTRO_MSG)


    async def help_command(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(self.HELP_MSG)



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


    async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        print(f'Update {update} caused error {context.error}')
        await update.message.reply_text("Sorry, this movie/show is unknown to me")
