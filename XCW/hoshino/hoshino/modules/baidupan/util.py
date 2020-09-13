# -*- coding: UTF-8 -*-
# from sqlitedict import SqliteDict
from nonebot import *
import yaml
import time
import json
import os
import re

bot = get_bot()


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dict_obj):
    if not isinstance(dict_obj, dict):
        return dict_obj
    inst = Dict()
    for k, v in dict_obj.items():
        inst[k] = dict_to_object(v)
    return inst


# 获取配置
def get_config():
    file = open(os.path.join(os.path.dirname(__file__), "config.yml"), 'r', encoding="utf-8")
    return dict_to_object(yaml.load(file.read(), Loader=yaml.FullLoader))


config = get_config()


# 获取字符串中的关键字
def get_msg_keyword(keyword, msg, is_first=False):
    msg = msg[0] if isinstance(msg, tuple) else msg
    res = re.split(format_reg(keyword, is_first), msg, 1)
    res = tuple(res[::-1]) if len(res) == 2 else False
    return ''.join(res) if is_first and res else res


# 格式化配置中的正则表达式
def format_reg(keyword, is_first=False):
    keyword = keyword if isinstance(keyword, list) else [keyword]
    return f"{'|'.join([f'^{i}' for i in keyword] if is_first else keyword)}"


def get_path(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


db = {}


# 初始化数据库
# def init_db(db_dir, db_name='db.sqlite') -> SqliteDict:
#     if db.get(db_name):
#         return db[db_name]
#     db[db_name] = SqliteDict(get_path(db_dir, db_name),
#                              encode=json.dumps,
#                              decode=json.loads,
#                              autocommit=True)
#     return db[db_name]


# 寻找MessageSegment里的某个关键字的位置
def find_ms_str_index(ms, keyword, is_first=False):
    for index, item in enumerate(ms):
        if item['type'] == 'text' and re.search(format_reg(keyword, is_first), item['data']['text']):
            return index
    return -1


# 是否是群管理员
def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def filter_list(plist, func):
    return list(filter(func, plist))


def is_admins(user_id: int) -> bool:
    admins = config.admins
    return user_id in set((admins if isinstance(admins, list) else [admins]) + bot.config.SUPERUSERS)


def size_format(size, is_disk=False, precision=2):
    formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    unit = 1000.0 if is_disk else 1024.0
    if not (isinstance(size, float) or isinstance(size, int)):
        raise TypeError('a float number or an integer number is required!')
    if size < 0:
        raise ValueError('number must be non-negative')
    for i in formats:
        size /= unit
        if size < unit:
            return f'{round(size, precision)}{i}'
    return f'{round(size, precision)}{i}'


class send_process:
    index = 0
    size = 0
    ctx = None
    msg_id = None

    def __init__(self, ctx, i, s):
        self.index = i
        self.size = s
        self.ctx = ctx

    async def send(self, msg=None):
        # try:
        #     if self.msg_id:
        #         time.sleep(1)  # 至少给1秒的休息机会
        #         await bot.delete_msg(message_id=self.msg_id)
        # except Exception as e:
        #     print(e)
        if msg:
            await self.__send__(msg)

    async def __send__(self, msg):
        self.index += 1
        if self.index > self.size:
            self.index = 1
        res = await bot.send(self.ctx, ''.join(['▓'] * self.index + ['░'] * (self.size - self.index)) + ' ' + msg)
        self.msg_id = res['message_id']


def escape(url: str, cq=None):
    url = url.replace(r'&', '&amp;') \
        .replace(r'\[', '&#91;').replace(r'\]', '&#93;')
    if cq:
        url = url.replace(r',', '&#44;') \
            .replace(r'(\ud83c[\udf00-\udfff])|(\ud83d[\udc00-\ude4f\ude80-\udeff])|[\u2600-\u2B55]', ' ')
    return url
