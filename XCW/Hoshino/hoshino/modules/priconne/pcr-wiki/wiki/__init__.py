from hoshino import config, Service, priv
from hoshino.typing import CQEvent
from .. import chara
from .data import *

sv_help = '''
- [@bot简介ue] 角色简介
- [@bot技能ue] 角色技能
- [@bot专武ue] 角色专武
- [@bot羁绊ue] 角色羁绊
'''.strip()

sv = Service(
    name = '公主连结wiki',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '查询', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助公主连结wiki"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


def get_chara(name, types):
    id_ = chara.name2id(name)
    confi = 100
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
    c = chara.fromid(id_)
    msg = ''
    is_npc = chara.is_npc(id_)
    if confi < 100:
        msg = f'兰德索尔似乎没有叫"{name}"的人...\n角色别称补全计划: github.com/Ice-Cirno/HoshinoBot/issues/5\n您有{confi}%的可能在找{guess_name}{c.icon.cqcode}'
    elif is_npc:
        msg = f'没有查询到{name}的wiki数据'
    else:
        msg = f'{c.icon.cqcode}'
        if types == 'introduce':
            msg = msg + get_info(id_)
        elif types == 'skill':
            msg = msg + get_skill(id_)
        elif types == 'uniquei':
            msg = msg + get_uniquei(id_)
        elif types == 'kizuna':
            msg = msg + get_kizuna(id_)
    return msg

@sv.on_prefix(('简介','介绍'), only_to_me=True)
async def introduce(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"简介"+别称，如"简介ue"')
        return
    result = get_chara(name,'introduce')
    await bot.send(ev, result)

@sv.on_prefix(('技能'), only_to_me=True)
async def skill(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"技能"+别称，如"技能ue"')
        return
    result = get_chara(name,'skill')
    await bot.send(ev, result)

@sv.on_prefix(('专武'), only_to_me=True)
async def uniquei(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"专武"+别称，如"专武ue"')
        return
    result = get_chara(name,'uniquei')
    await bot.send(ev, result)

@sv.on_prefix(('羁绊'), only_to_me=True)
async def kizuna(bot, ev: CQEvent):
    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"羁绊"+别称，如"羁绊ue"')
        return
    result = get_chara(name,'kizuna')
    await bot.send(ev, result)
