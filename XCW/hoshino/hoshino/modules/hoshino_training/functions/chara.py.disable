import os
import re
import json
import hoshino
import nonebot
import aiohttp
import random
import traceback
import csv
from ast import literal_eval

from hoshino.modules.hoshino_training.util.module import *

from hoshino.modules.priconne.chara import Roster, Chara
from hoshino.modules.priconne.gacha.gacha import Gacha

#可以在此加入自定义角色
#需要将头像命名为 icon_unit_[四位数ID]31.png 放置到 res\img\priconne\unit 目录
CUSTOM_CHARA = {
    3322: ['陈睿', 'チン エイ', '叔叔', '睿总', '二次元教父'],
}

startup_job = None

data = {
    'chara': {},
    'gacha': {},
}

pool_name = {
    'BL': {'BL', 'bl', 'Bl', 'bL', 'CN', 'cn'},
    'TW': {'TW', 'tw', 'so-net', 'sonet'},
    'JP': {'JP', 'jp'},
    'MIX': {'MIX', 'mix', 'Mix', 'All', 'all', 'ALL'}
}

jp = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]')

#查角色
class NewRoster(Roster):

    def __init__(self):
        super(NewRoster, self).__init__()
        self.update()

    def update(self):
        super(NewRoster, self).update()
        if 'chara' in data:
            for idx, names in data['chara'].items():
                for name in names:
                    name = hoshino.util.normalize_str(name)
                    if name not in self._roster:
                        self._roster[name] = idx
            self._all_name_list = self._roster.keys()

#角色信息
class NewChara(Chara):

    def __init__(self, id_, star=0, equip=0):
        super(NewChara, self).__init__(id_, star, equip)

    @property
    def name(self):
        name = super(NewChara, self).name
        if name == '未知角色' and self.id in data['chara']:
            name = data['chara'][self.id][0]
            if jp.search(name) and len(data['chara'][self.id]) > 1:
                name = data['chara'][self.id][1]
        return name

#抽卡
class NewGacha(Gacha):

    def __init__(self, pool_name:str = "MIX"):
        super(NewGacha, self).__init__(pool_name)

    def load_pool(self, pool_name:str):
        super(NewGacha, self).load_pool(pool_name)
        if 'gacha' in data and 'chara' in data and pool_name in data['gacha']:
            pool = data['gacha'][pool_name]
            self.up_prob = pool["up_prob"]
            self.s3_prob = pool["s3_prob"]
            self.s2_prob = pool["s2_prob"]
            self.s1_prob = 1000 - self.s2_prob - self.s3_prob
            self.up = pool["up"]
            self.star3 = pool["star3"]
            self.star2 = pool["star2"]
            self.star1 = pool["star1"]

async def query_data(url, is_json = False):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if is_json:
                    data = await resp.json()
                else:
                    data = await resp.text()
    except:
        traceback.print_exc()
        return None
    return data

def save_data():
    path = os.path.join(os.path.dirname(__file__), 'chara.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

def load_data():
    path = os.path.join(os.path.dirname(__file__), 'chara.json')
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding='utf8') as f:
            d = json.load(f)
            if 'gacha' in d:
                data['gacha'] = d['gacha']
            if 'chara' in d:
                data['chara'] = {}
                for k, v in d['chara'].items():
                    data['chara'][int(k)] = v
    except:
        traceback.print_exc()

def ids_to_names(id_list):
    name_list = []
    for id_ in id_list:
        chara = NewChara(id_)
        name_list.append(chara.name)
    return name_list

async def update_data():

    #pcrbot/pcr-nickname
    csv_data = await query_data('https://raw.fastgit.org/pcrbot/pcr-nickname/master/nicknames.csv')
    if csv_data:
        reader = csv.reader(csv_data.strip().split('\n'))
        for row in reader:
            if row[0].isdigit():
                row[1], row[2] = row[2], row[1]
                data['chara'][int(row[0])] = row[1:]

    #unitdata.py
    chara_data = await query_data('https://api.redive.lolikon.icu/gacha/unitdata.py')
    if chara_data:
        chara_data = chara_data.replace('CHARA_NAME = ', '')
        try:
            chara_data = literal_eval(chara_data)
        except:
            chara_data = {}
        for k, v in chara_data.items():
            if k in data['chara']:
                for sv in v:
                    if sv not in data['chara'][k]:
                        data['chara'][k].append(sv)
            else:
                data['chara'][k] = v
    
    #加入自定义角色
    for k, v in CUSTOM_CHARA.items():
        if k not in data['chara']:
            data['chara'][k] = v

    #update roster
    new_roster.update()

    #抽卡
    gacha_data = await query_data('https://api.redive.lolikon.icu/gacha/default_gacha.json', True)
    if chara_data:
        for k, v in gacha_data.items():
            if 'up' in v:
                v['up'] = ids_to_names(v['up'])
            if 'star1' in v:
                v['star1'] = ids_to_names(v['star1'])
            if 'star2' in v:
                v['star2'] = ids_to_names(v['star2'])
            if 'star3' in v:
                v['star3'] = ids_to_names(v['star3'])
            if k in pool_name['JP']:
                data['gacha']['JP'] = v
            elif k in pool_name['TW']:
                data['gacha']['TW'] = v
            elif k in pool_name['BL']:
                data['gacha']['BL'] = v
            #ALL池不使用

    save_data()

async def check_pool_update():
    global startup_job
    if startup_job:
        startup_job.remove()
        startup_job = None
    await update_data()

load_data()

new_roster = NewRoster()

module_replace('hoshino.modules.priconne.chara', 'roster', new_roster)
module_replace('hoshino.modules.priconne.chara', 'Chara', NewChara)
module_replace('hoshino.modules.priconne.gacha', 'Gacha', NewGacha)

startup_job = nonebot.scheduler.add_job(check_pool_update, 'interval', seconds=5)
nonebot.scheduler.add_job(check_pool_update, 'interval', hours=4)
