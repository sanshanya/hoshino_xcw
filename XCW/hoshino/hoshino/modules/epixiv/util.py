# -*- coding: UTF-8 -*-
from sqlitedict import SqliteDict
from nonebot import *
import uuid
import base64
import imghdr
import requests
import yaml
import json
import os
import re

bot = get_bot()


class Dict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value


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


def get_json(file_name):
    with open(get_path(file_name), 'r', encoding="utf-8") as file:
        return json.loads(file.read())


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
def init_db(db_dir, db_name='db', db_suffix='.sqlite') -> SqliteDict:
    if db.get(db_name):
        return db[db_name]
    db[db_name] = SqliteDict(get_path(db_dir, f'{db_name}{db_suffix}'),
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


# 是否是群管理员
def is_group_admin(ctx):
    return ctx['sender']['role'] in ['owner', 'admin', 'administrator']


def filter_list(plist, func):
    return list(filter(func, plist))


def get_illust_id(keyword):
    keyword = keyword.strip()
    if not keyword.isdigit():
        return None
    return int(keyword)
