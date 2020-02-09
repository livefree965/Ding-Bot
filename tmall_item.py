# encoding = utf-8
import os, json, re, time
import requests
from telegram.ext import Updater, CallbackContext, run_async
from database import Bot_Database, pcCode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from log import logger
import configparser


class Tmall_item():
    def __init__(self):
        self.notify_queue = {}
        self.job_online = []
        self.bot_database = Bot_Database()
        self.config = configparser.ConfigParser()
        self.success = 0
        self.failure = 0

    def match_tmall_share(self, update, context: CallbackContext):
        try:
            url = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                             update.message.text)[0]
            text = requests.get(url).text
            sku_id = re.findall('id=(.+?)&source', text) or re.findall('tmall\.com/i(.+?)\.htm', text) or re.findall(
                'taobao\.com/i(.+?)\.htm', text)
            sku_id = int(sku_id[0])
            chat_id = update.message.chat_id
            user_area = self.bot_database.get_user_area(chat_id)
            if not user_area:
                context.bot.send_message(update.message.chat_id, '请先通过/area 命令设置地区')
                return
            title = self.get_detail(sku_id, user_area)
            self.bot_database.add_user_sku(chat_id, sku_id)
            context.bot.send_message(update.message.chat_id, '添加商品监控:\n%s' % title)
        except:
            context.bot.send_message(update.message.chat_id, '识别失败')
            pass

    def reply_delete(self, update, context: CallbackContext):
        query = update.callback_query
        sku_id = int(query.data.split('_')[1])
        self.bot_database.del_user_sku(query.message.chat_id, sku_id)
        self.bot_database.del_has_notified(chat_id=query.message.chat_id, sku_id=sku_id)
        query.edit_message_text(text='删除商品成功')

    def delete_item(self, update, context: CallbackContext):
        keyboard = []
        watch_list = self.bot_database.get_user_watch(chat_id=update.message.chat_id)
        for sku_id, sku_title in watch_list:
            keyboard.append([InlineKeyboardButton(sku_title, callback_data='del_%s' % sku_id)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('请选择删除商品:', reply_markup=reply_markup)
        return

    def list_item(self, update, context: CallbackContext):
        chat_id = update.message.chat_id
        area_id = self.bot_database.get_user_area(chat_id)
        if not area_id:
            context.bot.send_message(update.message.chat_id, '请先通过/area 命令设置地区')
            return
        user_area = pcCode[area_id / 10000]
        list_msg = '地址: %s\n' % user_area
        for sku_id, sku_title in self.bot_database.get_user_watch(chat_id=chat_id):
            list_msg += '商品: %s\n' % (sku_title)
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='目前你监控商品列表如下:\n' + list_msg)
        pass

    @run_async
    def watch_one_sku_area(self, context: CallbackContext):
        sku_area = context.job.context
        sku_id, area_id = sku_area.split('_')
        sku_id = int(sku_id)
        area_id = int(area_id)
        while True:
            ret_res = self.if_item_can_buy(sku_id, area_id)
            if ret_res is True:
                chat_list = self.bot_database.get_notify_list(sku_id, area_id)
                if not chat_list:
                    return
                for chat_id in chat_list:
                    if not self.bot_database.has_notified(chat_id, sku_id):
                        area = pcCode[self.bot_database.get_user_area(chat_id) / 10000]
                        title = self.bot_database.get_sku_title(sku_id)
                        for i in range(3):
                            context.bot.send_message(chat_id=chat_id,
                                                     text='地址: %s\n商品: %s\n链接: %s' % (
                                                         area, title,
                                                         "https://detail.tmall.com/item.htm?id=%s" % sku_id))
                        self.bot_database.add_has_notified(chat_id, sku_id)
            elif ret_res is False and self.bot_database.isin_notified(sku_id):
                self.bot_database.del_has_notified(sku_id=sku_id)
            time.sleep(1)
            # break

    def notify_item(self, context: CallbackContext):
        for sku_id, area in self.bot_database.get_sku_area():
            sku_id = int(sku_id)
            area = int(area)
            sku_area = '%s_%s' % (sku_id, area)
            if sku_area not in self.job_online:
                context.job_queue.run_once(self.watch_one_sku_area, when=0.001, context=sku_area)
                self.job_online.append(sku_area)
                logger.info("%s 商品已添加至工作序列", sku_area)
        for sku_area in self.job_online:
            sku_id, area = sku_area.split('_')
            sku_id = int(sku_id)
            area = int(area)
            if not self.bot_database.get_notify_list(sku_id, area):
                self.job_online.remove(sku_area)
                logger.info("%s 商品已从工作序列删除", sku_area)
                continue

    def add_item(self, update, context: CallbackContext):
        try:
            sku_id, area = context.args
            self.add_notify_queue(sku_id, area, update.message.chat_id)
        except:
            context.bot.send_message(chat_id=update.message.chat_id, text='添加监控失败')
            return
        context.bot.send_message(chat_id=update.message.chat_id, text='添加监控成功')

    def set_area(self, update, context: CallbackContext):
        keyboard = []
        for i in range(7):
            keyboard.append([])
        for index, (key, value) in enumerate(pcCode.items()):
            keyboard[int(index / 5)].append(InlineKeyboardButton(value[:2], callback_data='area_%s' % key))
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('请选择地区:', reply_markup=reply_markup)
        return

    def reply_area(self, update, context: CallbackContext):
        query = update.callback_query
        area = int(query.data.split('_')[1] + '0000')
        self.bot_database.set_user_area(query.message.chat_id, area)
        query.edit_message_text(text='设置地区成功')

    def add_notify_queue(self, sku_id, area, chat_id):
        self.bot_database.add_user_sku(chat_id, sku_id)
        self.get_detail(sku_id, area)

    def get_detail(self, sku_id, area):
        res = self.bot_database.get_sku_title(sku_id)
        if res:
            return res
        else:
            while True:
                try:
                    ret_json = json.loads(requests.get(
                        "https://mdskip.m.tmall.com/mobile/queryH5Detail.htm?decision=sku&itemId=%s&areaId=%s" % (
                            sku_id, area)).text)
                    self.bot_database.set_sku_title(sku_id, ret_json['item']['title'])
                    return ret_json['item']['title']
                except:
                    logger.error("%s 访问详细页面失败" % sku_id)
                    pass

    def if_item_can_buy(self, sku_id, area):
        try:
            ret_json = json.loads(requests.get(
                "https://mdskip.m.tmall.com/mobile/queryH5Detail.htm?decision=sku&itemId=%s&areaId=%s" % (
                    sku_id, area)).text)
            return ret_json['trade']['buyEnable']
        except:
            logger.error("%s 访问API失败" % sku_id)
            return False

    @run_async
    def record_status(self, context: CallbackContext):
        res = self.bot_database.get_sku_area()
        if len(res) == 0:
            return
        sku_id, area = self.bot_database.get_sku_area()[0]
        try:
            ret_json = json.loads(requests.get(
                "https://mdskip.m.tmall.com/mobile/queryH5Detail.htm?decision=sku&itemId=%s&areaId=%s" % (
                    sku_id, area)).text)['trade']['buyEnable']
            self.success += 1
        except:
            self.failure += 1

    def get_status(self, update, context: CallbackContext):
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text='监控接口情况:\n成功:%d\n失败:%d' % (self.success, self.failure))
        return
