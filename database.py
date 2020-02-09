# encoding = utf-8
import sqlite3, os

pcCode = {11: '北京市', 12: '天津市', 13: '河北省', 14: '山西省', 15: '内蒙古自治区', 21: '辽宁省', 22: '吉林省',
          23: '黑龙江省', 31: '上海市', 32: '江苏省', 33: '浙江省', 34: '安徽省', 35: '福建省', 36: '江西省',
          37: '山东省', 41: '河南省', 42: '湖北省', 43: '湖南省', 44: '广东省', 45: '广西壮族自治区', 46: '海南省',
          50: '重庆市', 51: '四川省', 52: '贵州省', 53: '云南省', 54: '西藏自治区', 61: '陕西省', 62: '甘肃省',
          63: '青海省', 64: '宁夏回族自治区', 65: '新疆维吾尔自治区', 71: '台湾省', 81: '香港特别行政区', 82: '澳门特别行政区'}


class Bot_Database:
    def __init__(self):
        if os.path.exists('telegram.db'):
            self.conn = sqlite3.connect('telegram.db', check_same_thread=False)
            self.reset_has_notified()
        else:
            self.conn = sqlite3.connect('telegram.db', check_same_thread=False)
            self.init_database()
        self.conn.row_factory = lambda cursor, row: row

    def init_database(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE USER_AREA
        (CHAT_ID INT PRIMARY KEY NOT NULL,
        AREA_ID INT NOT NULL);''')
        c.execute('''CREATE TABLE AREA_MAP (
        AREA_ID INT PRIMARY KEY NOT NULL,
        AREA_NAME CHAR(4) NOT NULL);''')
        c.execute('''CREATE TABLE SKU_TITLE (
        SKU_ID INT PRIMARY KEY NOT NULL,
        TITLE VARCHAR(255) NOT NULL);''')
        c.execute('''CREATE TABLE USER_SKU(
        CHAT_ID INT NOT NULL,
        SKU_ID INT NOT NULL,
        PRIMARY KEY (CHAT_ID,SKU_ID));''')
        c.execute('''CREATE TABLE HAS_NOTIFIED(
                CHAT_ID INT NOT NULL,
                SKU_ID INT NOT NULL,
                PRIMARY KEY (CHAT_ID,SKU_ID));''')
        self.conn.commit()
        c.close()

    def reset_has_notified(self):
        c = self.conn.cursor()
        c.execute('''DELETE FROM HAS_NOTIFIED''')
        self.conn.commit()
        c.close()

    def set_user_area(self, chat_id, user_area):
        c = self.conn.cursor()
        c.execute('''REPLACE INTO USER_AREA (CHAT_ID,AREA_ID) VALUES (%d,%d)''' % (chat_id, user_area))
        self.conn.commit()
        c.close()

    def set_sku_title(self, sku_id, title):
        c = self.conn.cursor()
        c.execute('''REPLACE INTO SKU_TITLE (SKU_ID,TITLE) VALUES (%d,'%s' )''' % (sku_id, title))
        self.conn.commit()
        c.close()

    def close(self):
        self.conn.close()

    def add_has_notified(self, chat_id, sku_id):
        c = self.conn.cursor()
        c.execute('''REPLACE INTO HAS_NOTIFIED (CHAT_ID,SKU_ID) VALUES (%d,%d )''' % (chat_id, sku_id))
        self.conn.commit()
        c.close()

    def isin_notified(self, sku_id):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM HAS_NOTIFIED WHERE SKU_ID = %d;''' % (sku_id))
        res = c.fetchall()
        c.close()
        return False if not res else True

    def has_notified(self, chat_id, sku_id):
        c = self.conn.cursor()
        c.execute('''SELECT * FROM HAS_NOTIFIED WHERE CHAT_ID = %d AND SKU_ID = %d;''' % (chat_id, sku_id))
        res = c.fetchall()
        c.close()
        return False if not res else True

    def del_has_notified(self, chat_id=None, sku_id=None):
        c = self.conn.cursor()
        if chat_id is None:
            c.execute('''DELETE FROM HAS_NOTIFIED WHERE SKU_ID = %d;''' % (sku_id))
        else:
            c.execute('''DELETE FROM HAS_NOTIFIED WHERE SKU_ID = %d AND CHAT_ID = %d;''' % (sku_id, chat_id))
        self.conn.commit()
        c.close()

    def add_user_sku(self, chat_id, sku_id):
        c = self.conn.cursor()
        c.execute('''REPLACE INTO USER_SKU (CHAT_ID,SKU_ID) VALUES (%d,%d )''' % (chat_id, sku_id))
        self.conn.commit()
        c.close()

    def del_user_sku(self, chat_id, sku_id):
        c = self.conn.cursor()
        c.execute('''DELETE FROM USER_SKU WHERE CHAT_ID = %d AND SKU_ID = %d;''' % (chat_id, sku_id))
        self.conn.commit()
        c.close()

    def get_notify_list(self, sku_id, area):
        c = self.conn.cursor()
        c.execute(
            '''SELECT USER_SKU.CHAT_ID FROM USER_SKU inner join USER_AREA WHERE USER_SKU.CHAT_ID = USER_AREA.CHAT_ID AND SKU_ID = %d AND AREA_ID = %d;''' % (
                sku_id, area))
        res = c.fetchall()
        c.close()
        return [] if not res else res[0]

    def get_sku_title(self, sku_id):
        c = self.conn.cursor()
        c.execute(
            '''SELECT TITLE FROM SKU_TITLE WHERE SKU_ID = %d ''' % sku_id)
        res = c.fetchall()
        c.close()
        return [] if not res else res[0][0]

    def get_user_area(self, chat_id):
        c = self.conn.cursor()
        c.execute(
            '''SELECT AREA_ID FROM USER_AREA WHERE CHAT_ID = %d ''' % chat_id)
        res = c.fetchall()
        c.close()
        return [] if not res else res[0][0]

    def get_user_watch(self, chat_id):
        c = self.conn.cursor()
        c.execute(
            '''SELECT SKU_TITLE.SKU_ID,SKU_TITLE.TITLE FROM USER_SKU inner join SKU_TITLE WHERE USER_SKU.SKU_ID = SKU_TITLE.SKU_ID AND CHAT_ID = %d ;''' % (
                chat_id))
        res = c.fetchall()
        c.close()
        return res

    def get_sku_area(self):
        c = self.conn.cursor()
        c.execute(
            '''SELECT USER_SKU.SKU_ID,USER_AREA.AREA_ID FROM USER_SKU inner join USER_AREA WHERE USER_SKU.CHAT_ID = USER_AREA.CHAT_ID;''')
        res = c.fetchall()
        c.close()
        return res
