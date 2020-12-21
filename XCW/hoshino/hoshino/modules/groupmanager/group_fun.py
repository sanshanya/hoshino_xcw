from hoshino import Service, priv, R
from hoshino.util import DailyNumberLimiter

import random

from . import util

sv = Service('群管plus', visible= True, enable_on_default= True, bundle='群管plus', help_='''
- [谁是龙王] 迫害龙王
- [@bot 送礼物@sb] 让bot送sb礼物
- [@bot 饿饿] 让bot送自己礼物
'''.strip())


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
        

@sv.on_prefix(('送礼物','，土豪，我也要礼物~','给我礼物','我要礼物','要礼物','饿饿'),only_to_me=True)
async def send_gift(bot, ev):
    uid = ev.user_id
    sid = None
    gid = ev.group_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '这种事情做不到啦~', at_sender=True)
            return
    if sid is None:
        sid = uid
    await bot.send(ev, f'[CQ:gift,qq={sid},id={random.randint(0,13)}]')
    