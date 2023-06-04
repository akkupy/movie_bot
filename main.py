__author__ = "Akkupy"
__license__ = "GNU GPL v.3"
__maintainer__ = "Akkupy"
__status__ = "Maintenance"

from telegram.ext import CommandHandler,MessageHandler,filters,CallbackQueryHandler,PrefixHandler

from src import Bot

def main():

    bot = Bot()
    bot.app.add_handler(CommandHandler('start', bot.start_command))
    
    bot.app.add_handler(CommandHandler("find", bot.find_title))

    bot.app.add_handler(MessageHandler(filters.TEXT, bot.any_text))

    bot.app.add_error_handler(bot.error)

    bot.app.add_handler(CallbackQueryHandler(bot.query_handler))

    print('Polling...')
    
    bot.app.run_polling(poll_interval=3)






if __name__ == '__main__':
    main()