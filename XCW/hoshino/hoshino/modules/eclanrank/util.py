# -*- coding: UTF-8 -*-
from sqlitedict import SqliteDict
from nonebot import *
import math
import yaml
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
    file = open(os.path.join(os.path.dirname(__file__), "config.yaml"), 'r', encoding="utf-8")
    return dict_to_object(yaml.load(file.read(), Loader=yaml.FullLoader))


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
def init_db(db_dir, db_name='db.sqlite') -> SqliteDict:
    if db.get(db_name):
        return db[db_name]
    db[db_name] = SqliteDict(get_path(db_dir, db_name),
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


# 获取群内的群友名字
async def get_group_member_name(group_id, user_id):
    qq_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
    return qq_info['card'] or qq_info['nickname']


bossData = {
    'scoreRate': [
        [1, 1, 1.3, 1.3, 1.5],
        [1.4, 1.4, 1.8, 1.8, 2],
        [2.0, 2.0, 2.5, 2.5, 3.0]
    ],
    'hp': [6000000, 8000000, 10000000, 12000000, 20000000],
    'max1': 4,
    'max2': 11
}


def calc_hp(hp_base: int):
    zm = 1
    king = 1
    cc = 0.0
    remain = 0.0
    damage = 0
    remainHp = 0.0
    remainPer = 0.0

    while True:
        if zm < bossData['max1']:
            nowZm = 0
        elif bossData['max1'] <= zm < bossData['max2']:
            nowZm = 1
        elif zm >= bossData['max2']:  
            nowZm = 2
        #nowZm = bossData['max1'] - 1 if zm > bossData['max1'] else zm - 1
        cc += bossData['scoreRate'][nowZm][king - 1] * bossData['hp'][king - 1]
        if cc > hp_base:
            cc -= bossData['scoreRate'][nowZm][king - 1] * bossData['hp'][king - 1]
            remain = (hp_base - cc) / bossData['scoreRate'][nowZm][king - 1]
            damage += remain
            remainPer = 1.0 - remain / bossData['hp'][king - 1]
            remainHp = bossData['hp'][king - 1] - remain
            break
        damage += bossData['hp'][king - 1]
        if king == 5:
            zm += 1
            king = 1
            continue
        king += 1
    remainPer *= 100
    bdk = bossData['hp'][king - 1]
    return f'{zm}周目{king}王 [{math.floor(remainHp)}/{bdk}]  {round(remainPer, 2)}%'