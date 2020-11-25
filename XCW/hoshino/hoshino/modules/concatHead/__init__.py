import base64
import pickle
import os
from io import BytesIO
from os import path

import aiohttp
from PIL import Image

from .._res import Res as R
from hoshino.service import Service
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.util import DailyNumberLimiter, FreqLimiter
from .._util import extract_url_from_event
from .config import *
from .data_source import detect_face, concat, KyaruHead, auto_head, gen_head

conf_path = path.join(path.dirname(__file__), 'user_conf')
sv = Service('接头霸王')
_nlt = DailyNumberLimiter(DAILY_MAX_NUM)
_flt = FreqLimiter(30)

try:
    with open(conf_path, 'rb') as f:
        user_conf_dic = pickle.load(f)
except FileNotFoundError:
    user_conf_dic = {}

@sv.on_prefix(('接头霸王', '接头'))
async def concat_head(bot: HoshinoBot, ev: CQEvent):
    uid = ev.user_id
    if not _nlt.check(uid):
        await bot.finish(ev, '今日已经到达上限！')

    if not _flt.check(uid):
        await bot.finish(ev, '太频繁了，请稍后再来')

    url = extract_url_from_event(ev)
    if not url:
        await bot.finish(ev, '请附带图片!')
    url = url[0]
    await bot.send(ev, '请稍等片刻~')

    _nlt.increase(uid)
    _flt.start_cd(uid, 30)

    # download picture and generate base64 str
    # b百度人脸识别api无法使用QQ图片服务器的图片，所以使用base64
    async with  aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            cont = await resp.read()
            b64 = (base64.b64encode(cont)).decode()
            img = Image.open(BytesIO(cont))

    face_data_list = await detect_face(b64)
    #print(face_data_list)
    if not face_data_list:
        await bot.finish(ev, '未检测到人脸信息')

    uid = ev.user_id
    head_name = user_conf_dic.get(uid, 'auto')
    output = '' ######
    head_gener = gen_head()
    for dat in face_data_list:
        if head_name == 'auto':
            #head = auto_head(dat)
            head = head_gener.__next__() 
        else:
            head = KyaruHead.from_name(head_name)
        output = concat(img, head, dat)
    pic = R.image_from_memory(output)
    #print(pic)
    await bot.send(ev, pic)


@sv.on_prefix('选头')
async def choose_head(bot: HoshinoBot, ev: CQEvent):
    global user_conf_dic
    uid = ev.user_id
    head_name = ev.raw_message.strip(ev.prefix)
    if head_name == 'auto':
        user_conf_dic[uid] = 'auto'
        with open(conf_path, 'wb') as f:
            pickle.dump(user_conf_dic, f)
        await bot.finish(ev, '已切换为自动选头')

    user_conf_dic[uid] = head_name
    if not KyaruHead.exist_head(head_name):
        await bot.finish(ev, '没有这个头哦~')
    with open(conf_path, 'wb') as f:
        pickle.dump(user_conf_dic, f)
    head = KyaruHead.from_name(head_name)
    await bot.send(ev, f'猫猫头已经切换为{head.cqcode}')



