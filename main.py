__author__ = "Akkupy"
__license__ = "GNU GPL v.3"
__maintainer__ = "Akkupy"
__status__ = "Maintenance"

from telegram.ext import CommandHandler,MessageHandler,filters,CallbackQueryHandler

from src import Botz

def main():

    print(r'''
     __       _       _           
    /  \     | |     | | 
   /    \    | | /\  | | /\   _   _
  /  /\  \   | |/ /  | |/ /  | | | |  
 /  ____  \  | |\ \  | |\ \  | |_| |
/__/    \__\ |_| \_\ |_| \_\  \___/  ''')
    print("\n*************************************")
    print("\n* Copyright of akkupy, 2023         *")
    print("\n* https://www.github.com/akkupy     *")
    print("\n* https://t.me/akkupy               *")
    print("\n*************************************\n\n\n")

    bot = Botz()
    bot.app.add_handler(CommandHandler('start', bot.start_command))

    bot.app.add_handler(CommandHandler('help', bot.help_command))

    bot.app.add_handler(CommandHandler("find", bot.find_title))

    bot.app.add_handler(CommandHandler("save", bot.movie_saver))

    bot.app.add_handler(CommandHandler("remove", bot.movie_remover))

    bot.app.add_handler(CommandHandler("list", bot.movie_list))

    bot.app.add_handler(CommandHandler("reboot", bot.reboot))

    bot.app.add_handler(CommandHandler("status", bot.status))

    bot.app.add_handler(MessageHandler(filters.TEXT, bot.any_text))

    bot.app.add_error_handler(bot.error)

    bot.app.add_handler(CallbackQueryHandler(bot.query_handler))

    print('Bot Started Polling! Check Terminal for Errors')
    
    bot.app.run_polling(poll_interval=3)




if __name__ == '__main__':
    main()