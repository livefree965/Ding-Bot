# encoding = utf-8
import os
import configparser
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from tmall_item import *


class Bot_Controller:
    def __init__(self):
        self.load_config()

    def set_bot(self, bot):
        self.bot = bot
        self.updater = Updater(use_context=True, bot=bot, workers=1024)

    def start(self, update, context):
        update.message.reply_text('欢迎光临~目前机器人还在Debug阶段，监控效果仅供参考）\n'
                                  '使用说明:\n'
                                  '1.输入 / 即可获得提示，使用前需要跟我说/area设置地区\n'
                                  '2.支持淘宝分享链接支持复制给我添加，只要带有m.tb.cn我都可以识别哒，例如：\n'
                                  '付致这行话转移至τаo宝аρρ；或https://m.tb.cn/xxx 嚸↑↓擊鏈﹏接，再选择瀏覽→\n'
                                  '3.有任何想法可以搜索@sysu_bot向我提问或建议\n'
                                  '4.非常感谢支持')

    def unknown_command(self, update, context):
        update.message.reply_text('没听懂哦，输入/start获取帮助')

    def set_tmall_handler(self):
        self.tmall_item = Tmall_item()
        self.updater.job_queue.run_repeating(self.tmall_item.notify_item, interval=5, first=0)
        self.updater.job_queue.run_repeating(self.tmall_item.record_status, interval=60, first=0)
        self.updater.dispatcher.add_handler(MessageHandler(Filters.regex('m.tb.cn'), self.tmall_item.match_tmall_share))
        self.updater.dispatcher.add_handler(CommandHandler('start', self.start))
        self.updater.dispatcher.add_handler(CommandHandler('list', self.tmall_item.list_item))
        self.updater.dispatcher.add_handler(CommandHandler('del', self.tmall_item.delete_item))
        self.updater.dispatcher.add_handler(CommandHandler('area', self.tmall_item.set_area))
        self.updater.dispatcher.add_handler(CommandHandler('status', self.tmall_item.get_status))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tmall_item.reply_area, pattern='area'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tmall_item.reply_delete, pattern='del'))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text, self.unknown_command))

    def start_polling(self):
        self.updater.start_polling()

    def load_config(self):
        self.config = configparser.ConfigParser()
        if not os.path.exists('config.ini'):
            self.config['Bot_config'] = {'token': '', 'proxy_url': ''}
            with open('config.ini', 'w') as f:
                self.config.write(f)
            print('请设置config.ini')
            exit(0)
        else:
            self.config.read('config.ini')
            self.token = self.config['Bot_config']['token']
            self.proxy_url = self.config['Bot_config']['proxy_url']
            if self.token == '':
                print('请设置config.ini')
                exit(0)
