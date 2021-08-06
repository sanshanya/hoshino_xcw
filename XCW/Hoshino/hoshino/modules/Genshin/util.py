# -*- coding: UTF-8 -*-
import datetime
import base64
import functools
import time
import yaml
import json
import os
import re
from io import BytesIO

from PIL import ImageFont
from sqlitedict import SqliteDict
from pathlib import Path
from nonebot import *

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
def get_config(name='config.yml'):
    file = open(os.path.join(os.path.dirname(__file__), str(Path(name))), 'r', encoding="utf-8")
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
def init_db(db_dir, db_name='db.sqlite', tablename='unnamed') -> SqliteDict:
    if db.get(db_name):
        return db[db_name]
    db[db_name] = SqliteDict(get_path(db_dir, db_name),
                             tablename=tablename,
                             encode=json.dumps,
                             decode=json.loads,
                             autocommit=True)
    return db[db_name]


# 寻找MessageSegment里的某个关键字的位置
def find_ms_str_index(ms, keyword, is_first=False):
    for index, item in enumerate(ms):
        if item['type'] == 'text' and re.search(format_reg(keyword, is_first), item['data']['text']):
            return index
    return -1


def filter_list(plist, func):
    return list(filter(func, plist))


def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def get_next_day():
    return time.mktime((datetime.date.today() + datetime.timedelta(days=+1)).timetuple()) + 1000


def get_font(size):
    return ImageFont.truetype(get_path('assets', 'font', 'HYWenHei 85W.ttf'), size=size)


def pil2b64(data):
    bio = BytesIO()
    data = data.convert("RGB")
    data.save(bio, format='JPEG', quality=80)
    base64_str = base64.b64encode(bio.getvalue()).decode()
    return 'base64://' + base64_str


def cache(ttl=datetime.timedelta(hours=1), arg_key=None):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            default_data = {"time": None, "value": None}
            ins_key = 'default'
            if arg_key:
                ins_key = arg_key + str(kw.get(arg_key, ''))
                data = cache_data.get(ins_key, default_data)
            else:
                data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data['time'] or now - data['time'] > ttl:
                data['value'] = await func(*args, **kw)
                data['time'] = now
                cache_data[ins_key] = data

            return data['value']

        return wrapped

    return wrap
