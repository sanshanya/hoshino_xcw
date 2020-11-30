from hoshino import Service, priv, R
from hoshino.util import DailyNumberLimiter

import random

from . import util

sv = Service('group-manager', enable_on_default=True, visible=True)

@sv.on_prefix('申请头衔')
async def special_title(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    title = ev.message.extract_plain_text()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.title_get(bot, ev, uid, sid, gid, title)

#go-cqhttp似乎暂时不支持收回专属头衔...
@sv.on_fullmatch(('删除头衔','清除头衔','收回头衔','回收头衔','取消头衔'))
async def del_special_title(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    title = None
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.title_get(bot, ev, uid, sid, gid, title)

@sv.on_prefix(('来发口球','塞口球','禁言一下','禁言','口球','黑屋'))
async def umm_ahh(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    time = ev.message.extract_plain_text().strip()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await util.gruop_silence(bot, ev, gid, True)
            return
    if sid is None:
        sid = uid
    await util.member_silence(bot, ev, uid, sid, gid, time)

@sv.on_prefix(('解除口球','取消口球','摘口球','脱口球','取消禁言','解除禁言','摘下口球','解禁'))
async def cancel_ban_member(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    sid = None
    time = '0'
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await util.gruop_silence(bot, ev, gid, False)
            return
    if sid is None:
        await bot.send(ev, '请@需要摘口球的群员哦w')
        return
    await util.member_silence(bot, ev, uid, sid, gid, time)

@sv.on_fullmatch(('全员口球','全员禁言'))
async def ban_all(bot, ev):
    gid = ev.group_id
    status = True
    await util.gruop_silence(bot, ev, gid, status)

@sv.on_fullmatch(('取消全员口球','取消全员禁言','解除全员口球','解除全员禁言'))
async def cancel_ban_all(bot, ev):
    gid = ev.group_id
    status = False
    await util.gruop_silence(bot, ev, gid, status)

@sv.on_prefix(('来张飞机票','踢出本群','移出本群','踢出此群','移出群聊','飞机票','飞机','滚'))
async def guoup_kick(bot, ev):
    uid = ev.user_id
    gid = ev.group_id
    sid = None
    is_reject = False
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    await util.member_kick(bot, ev, uid, sid, gid, is_reject)

@sv.on_prefix(('修改名片','修改群名片','设置名片','设置群名片'))
async def card_set(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    card_text = ev.message.extract_plain_text()
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
    if sid is None:
        sid = uid
    await util.card_edit(bot, ev, uid, sid, gid, card_text)
    
@sv.on_fullmatch(('谁是龙王','迫害龙王','龙王是谁'))
async def whois_dragon_king(bot, ev):
    gid = ev.group_id
    self_info = await util.self_member_info(bot, ev, gid)
    sid = self_info['user_id']
    honor_type = 'talkative'
    ta_info = await util.honor_info(bot, ev, gid, honor_type)
    if 'current_talkative' not in ta_info:
        await bot.send(ev, '本群没有开启龙王标志哦~')
        return
    dk = ta_info['current_talkative']['user_id']
    if sid == dk:
        pic = R.img('dk_is_me.jpg').cqcode
        await bot.send(ev,f'啊，我是龙王\n{pic}')
    else:
        action=random.choice(['龙王出来挨透','龙王出来喷水'])
        dk_avater = ta_info['current_talkative']['avatar'] + '640' + f'&t={dk}'
        await bot.send(ev, f'[CQ:at,qq={dk}]\n{action}\n[CQ:image,file={dk_avater}]')

@sv.on_prefix(('修改群名','设置群名'))
async def set_group_name(bot, ev):
    gid = ev.group_id
    uid = ev.user_id
    name_text = ev.message.extract_plain_text()
    await util.group_name(bot, ev, gid, name_text)