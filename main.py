from telegram import Bot
from telegram.utils import request
from Bot_Controller import *

if __name__ == "__main__":
    bot_controller = Bot_Controller()
    if bot_controller.proxy_url == '':
        proxy = request.Request(con_pool_size=1028)
    else:
        proxy = request.Request(proxy_url=bot_controller.proxy_url, con_pool_size=8)
    bot = Bot(token=bot_controller.token, request=proxy)
    bot_controller.set_bot(bot)
    bot_controller.set_tmall_handler()
    bot_controller.start_polling()
