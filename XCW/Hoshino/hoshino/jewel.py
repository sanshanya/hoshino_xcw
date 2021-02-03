import base64
import os
import sqlite3

jewel_DB_PATH = os.path.expanduser('~/.hoshino/jewel.db')
'''
如何使用宝石系统
对某插件加上 from hoshino import jewel
这是触发示例:
    try:
        jewel_counter = jewel.jewelCounter()
        gid = ev.group_id
        uid = ev.user_id
        current_jewel = jewel_counter._get_jewel(gid, uid)  获取当前宝石数 
        jewel_counter._add_jewel(gid, uid, num) 增加num的宝石
        jewel_counter._reduce_jewel(gid, uid, num) 减少num的宝石
        jewel_counter._judge_jewel(gid, uid, input_jewel) 对比现有宝石与input_jewel如果前者大返回1后者大返回0 
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))
'''


class jewelCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(jewel_DB_PATH), exist_ok=True)
        self._create_table()
    def _connect(self):
        return sqlite3.connect(jewel_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS jewelCOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           jewel           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _add_jewel(self, gid, uid, jewel):
        try:
            current_jewel = self._get_jewel(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO jewelCOUNTER (GID,UID,jewel) \
                                VALUES (?,?,?)", (gid, uid, current_jewel + jewel))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _reduce_jewel(self, gid, uid, jewel):
        try:
            current_jewel = self._get_jewel(gid, uid)
            if current_jewel >= jewel:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO jewelCOUNTER (GID,UID,jewel) \
                                VALUES (?,?,?)", (gid, uid, current_jewel - jewel))
                conn.commit()
            else:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO jewelCOUNTER (GID,UID,jewel) \
                                VALUES (?,?,?)", (gid, uid, 0))
                conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_jewel(self, gid, uid):
        try:
            r = self._connect().execute("SELECT jewel FROM jewelCOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    def _judge_jewel(self, gid, uid, jewel):
        try:
            current_jewel = self._get_jewel(gid, uid)
            if current_jewel >= jewel:
                return 1
            else:
                return 0
        except Exception as e:
            raise Exception(str(e))
