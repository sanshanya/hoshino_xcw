# HoshinoBot\hoshino\modules\groupmaster\anti_holo.py
import os
import random
from datetime import timedelta
from hoshino import Service, priv, util, R, HoshinoBot
from hoshino.typing import CQEvent

from hoshino.modules.hoshino_training.util.module import *
from hoshino.modules.hoshino_training.util.keyword import *

#从HoshinoBot\hoshino\modules\groupmaster\anti_holo.py的SB_HOLO触发词中删除指定词语
WHITE_LIST = '''
可可
'''.split()

#额外的anti-holo触发词
BLACK_LIST = '''
神楽 神乐 めあ かぐら mea 屑女仆
'''.split()

def get_origin_tiangou_pic():
    res = R.img('hahaha_vtb_tiangou.jpg')
    if os.path.exists(res.path):
        return res
    else:
        return None

def get_tiangou_pic():
    path = f'anti-holo'
    res = R.img(path)
    if not os.path.exists(res.path):
        return get_origin_tiangou_pic()
    fnlist = os.listdir(res.path)
    if len(fnlist) == 0:
        return get_origin_tiangou_pic()
    fn = random.choice(fnlist)
    path = f'anti-holo/' + fn
    return R.img(path)
    

async def anti_holo(bot: HoshinoBot, ev: CQEvent):
    priv.set_block_user(ev.user_id, timedelta(minutes=1))
    await util.silence(ev, 60, skip_su=False)
    pic = get_tiangou_pic()
    if pic:
        await bot.send(ev, pic.cqcode)
    else:
        await bot.send(ev, 'vtb舔狗,爬!')
    await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)

SB_HOLO = module_get('hoshino.modules.groupmaster.anti_holo', 'SB_HOLO')
if SB_HOLO:
    keyword_replace(SB_HOLO, anti_holo)
    keyword_remove(WHITE_LIST)
    keyword_add(BLACK_LIST, SB_HOLO)
