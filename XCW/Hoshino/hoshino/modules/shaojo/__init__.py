import random
from hoshino import Service, util, priv
from hoshino.typing import CQEvent
import time
from .choicer import Choicer

sv_help = '''
今天我要变成少女!
今天你是什么少女
'''.strip()

sv = Service(
    name = '今天也是少女',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助今天也是少女"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

inst = Choicer(util.load_config(__file__))

@sv.on_fullmatch('今天我是什么少女')
async def my_shoujo(bot, ev: CQEvent):
    uid = ev.user_id
    name = ev.sender['card'] or ev.sender['nickname']
    msg = inst.format_msg(uid, name)
    await bot.send(ev, msg)


@sv.on_prefix('今天你是什么少女')
@sv.on_suffix('今天你是什么少女')
async def other_shoujo(bot, ev: CQEvent):
    arr = []
    for i in ev.message:
        if i['type'] == 'at' and i['data']['qq'] != 'all':
            arr.append(int(i['data']['qq']))
    gid = ev.group_id
    for uid in arr:
        info = await bot.get_group_member_info(
                group_id=gid,
                user_id=uid,
                no_cache=True
        )
        name = info['card'] or info['nickname']
        msg = inst.format_msg(uid, name)
        await bot.send(ev, msg)
