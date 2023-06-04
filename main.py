__author__ = "Akkupy"
__license__ = "GNU GPL v.3"
__maintainer__ = "Akkupy"
__status__ = "Maintenance"

from telegram.ext import CommandHandler,MessageHandler,filters,CallbackQueryHandler

from src import Bot

def main():

    bot = Bot()
    bot.app.add_handler(CommandHandler('start', bot.start_command))
    bot.app.add_handler(CommandHandler('help', bot.help_command))
    # bot.app.add_handler(CommandHandler("find", bot.find_title))
    # bot.app.add_handler(CommandHandler("rate", bot.rated))
    # bot.app.add_handler(CommandHandler("rated", bot.rated))
    # bot.app.add_handler(CommandHandler("language", bot.language))
    # bot.app.add_handler(CommandHandler("languages", bot.language))
    # bot.app.add_handler(CommandHandler("award", bot.awards))
    # bot.app.add_handler(CommandHandler("awards", bot.awards))
    # bot.app.add_handler(CommandHandler("plot", bot.plot))
    # bot.app.add_handler(CommandHandler("rating", bot.rating))
    # bot.app.add_handler(CommandHandler("ratings", bot.rating))
    # bot.app.add_handler(CommandHandler("link", bot.link))

    # bot.app.add_handler(MessageHandler(filters.TEXT, handle_message))

    bot.app.add_error_handler(bot.error)

    # bot.app.add_handler(CallbackQueryHandler(bot.query_handler))

    print('Polling...')
    
    bot.app.run_polling(poll_interval=3)






if __name__ == '__main__':
    main()