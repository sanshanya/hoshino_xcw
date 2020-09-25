import hoshino
import asyncio
from hoshino import Service, aiorequests, priv
from hoshino.util import FreqLimiter, DailyNumberLimiter
from .request import *
from .config import DAILY_MAX_NUM, FREQ_LIMIT

sv = Service('setu_acggov', bundle='pcr娱乐', enable_on_default=False, manage_priv = priv.SUPERUSER, help_='随机涩图/setu [n]\n本日涩图排行榜 [page]\n看涩图 [n] 或 [start end]')

#设置limiter
tlmt = DailyNumberLimiter(DAILY_MAX_NUM)
flmt = FreqLimiter(FREQ_LIMIT)

def check_lmt(uid, num):
    if uid in hoshino.config.SUPERUSERS:
        return 0, ''
    if not tlmt.check(uid):
        return 1, f'您今天已经冲过{DAILY_MAX_NUM}次了,请明天再来!'
    if num > 1 and (DAILY_MAX_NUM - tlmt.get_num(uid)) < num:
            return 1, f'您今天的剩余次数为{DAILY_MAX_NUM - tlmt.get_num(uid)}次,已不足{num}次,请少冲一点!'
    if not flmt.check(uid):
        return 1, f'您冲的太快了,请等待{round(flmt.left_time(uid))}秒!'
    tlmt.increase(uid,num)
    flmt.start_cd(uid)
    return 0, ''


@sv.on_prefix(['随机涩图', 'setu'])
async def send_setu(bot, ev):
    num = ev.message.extract_plain_text()
    if not num.isdigit():
        num = 1
    num = int(num)
    uid = ev['user_id']
    result, msgs = check_lmt(uid, num)
    if result != 0:
        await bot.send(ev, msgs)
        return
    for _ in range(num):
        _, pic = await get_setu()
        msg = await bot.send(ev, pic)
        await asyncio.sleep(SHOW_TIME)
        await bot.delete_msg(message_id=msg['message_id'])

@sv.on_prefix('本日涩图排行榜')
async def send_ranking(bot, ev):
    page = ev.message.extract_plain_text()
    if not page.isdigit():
        page = 1
    page = int(page)
    page -= 1
    if page < 0:
        page = 0
    _, msg = await get_ranking(page)
    await bot.send(ev, msg)

@sv.on_prefix('看涩图')
async def send_ranking_setu(bot, ev):
    uid = ev['user_id']
    start = 0
    end = 0
    args = ev.message.extract_plain_text().split()
    if len(args) > 0 and args[0].isdigit():
        start = int(args[0])
        start -= 1
        if start < 0:
            start = 0
        end = start + 1
    if len(args) > 1 and args[1].isdigit():
        end = int(args[1])
    result, msgs = check_lmt(uid, end - start)
    if result != 0:
        await bot.send(ev, msgs)
        return
    for i in range(start, end):
        _, pic = await get_setu()
        msg = await bot.send(ev, pic)
        await asyncio.sleep(SHOW_TIME)
        await bot.delete_msg(message_id=msg['message_id'])

