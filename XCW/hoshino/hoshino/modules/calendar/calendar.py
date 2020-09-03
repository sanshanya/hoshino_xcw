import os
import datetime
from collections import defaultdict
from .event import Event

from hoshino import Service, priv, util, log
from hoshino.typing import *
import nonebot
try:
    import ujson as json
except:
    import json

sv_help = '''
[日历|本周日历|今日日历|明日日历] 查看日程表
[切换日程] 切换日程表地区
[设置日程时间] 切换日程表每日推送时间
[查看日程地区] 查看本群日程表地区
[查看日程时间] 查看本群日程表推送时间
[停止推送日程] 停止推送日程
[开始推送日程] 开始推送日程
'''.strip()
sv = Service('calendar', help_=sv_help, bundle='pcr查询')

logger = log.new_logger('calendar')

CALENDAR = ('cn', 'tw', 'jp')
DEFAULT_CALENDAR = {"calendar_region":CALENDAR[0], "time":"08:00", "enable":True}

_calendar_config_file = os.path.expanduser('~/.hoshino/group_calendar_config.json')
_group_calendar = {}
try:
    with open(_calendar_config_file, encoding='utf8') as f:
        _group_calendar = json.load(f)
except FileNotFoundError as e:
    logger.warning('group_calendar_config.json not found, will create when needed.')
_group_calendar = defaultdict(lambda: DEFAULT_CALENDAR, _group_calendar)

def dump_calendar_config():
    with open(_calendar_config_file, 'w', encoding='utf8') as f:
        json.dump(_group_calendar, f, ensure_ascii=False)

CALENDAR_NAME_TIP = '请选择以下日程表\n> 切换日程jp\n> 切换日程tw\n> 切换日程cn'
@sv.on_prefix(('切换日程', '选择日程', '设置日程', '设定日程'))
async def set_calendar(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能切换日程', at_sender=True)
    name = util.normalize_str(ev.message.extract_plain_text())
    if not name:
        await bot.finish(ev, CALENDAR_NAME_TIP, at_sender=True)
    elif name in ('b', 'b服', 'bl', 'bilibili', '国', '国服', 'cn'):
        name = 'cn'
        reply = '国服'
    elif name in ('台', '台服', 'tw', 'sonet'):
        name = 'tw'
        reply = '台服'
    elif name in ('日', '日服', 'jp', 'cy', 'cygames'):
        name = 'jp'
        reply = '日服'
    else:
        await bot.finish(ev, f'未知服务器地区 {CALENDAR_NAME_TIP}', at_sender=True)
    gid = str(ev.group_id)
    _group_calendar[gid].update({"calendar_region": name})
    dump_calendar_config()
    await bot.send(ev, f'日程表已切换为{reply}', at_sender=True)

@sv.on_prefix(('切换日程时间', '选择日程时间', '设置日程时间', '设定日程时间'))
async def set_time(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能更改推送时间', at_sender=True)
    time = util.normalize_str(ev.message.extract_plain_text())
    try:
        datetime.datetime.strptime(time, '%H:%M')
    except ValueError:
        await bot.finish(ev, f'时间{time}格式不正确，示例：切换日程时间08:00', at_sender=True)
    gid = str(ev.group_id)
    _group_calendar[gid].update({"time": time, "enable":True})
    dump_calendar_config()
    await bot.send(ev, f'日程表推送时间已更改为每日{time}', at_sender=True)

@sv.on_fullmatch('查看日程地区')
async def get_calendar(bot, ev: CQEvent):
    gid = str(ev.group_id)
    service = _group_calendar[gid]['calendar_region']
    if service == 'cn':
        reply = '国服'
    elif service == 'tw':
        reply = '台服'
    elif service == 'jp':
        reply = '日服'
    await bot.send(ev, f"当前设置为{reply}日程表", at_sender=True)

@sv.on_fullmatch('查看日程时间')
async def get_time(bot, ev: CQEvent):
    gid = str(ev.group_id)
    time = _group_calendar[gid]['time']
    await bot.send(ev, f"本群日程表推送时间为每日{time}", at_sender=True)

@sv.on_suffix(('日历','日程表','日程'))
@sv.on_prefix(('日历','日程表','日程'))
async def calendar(bot, ev: CQEvent):
    gid = str(ev.group_id)
    kw = ev.message.extract_plain_text().strip()
    if not kw or kw in ('一周', '本周', '这周'):
        result = await Event(_group_calendar[gid]).get_week_events()
        await bot.send(ev, f"{result}")
    elif kw in ('今日', '今天', '本日'):
        result = await Event(_group_calendar[gid]).send_daily_async(2)
        await bot.send(ev, f"{result}")
    elif kw in ('明日', '明天'):
        result = await Event(_group_calendar[gid]).send_daily_async(3)
        await bot.send(ev, f"{result}")

@sv.on_fullmatch('停止推送日程')
async def stop_scheduled(bot, ev: CQEvent):
    gid = str(ev.group_id)
    _group_calendar[gid].update({"enable":False})
    dump_calendar_config()
    await bot.send(ev, f"停止推送日程", at_sender=True)

@sv.on_fullmatch('开始推送日程')
async def start_scheduled(bot, ev: CQEvent):
    gid = str(ev.group_id)
    _group_calendar[gid].update({"enable":True})
    dump_calendar_config()
    await bot.send(ev, f"开始推送日程", at_sender=True)

@nonebot.scheduler.scheduled_job('interval', minutes = 1)
async def scheduled_job():
    for key in _group_calendar:
        time = _group_calendar[key].get('time', '08:00')
        flag = datetime.datetime.now().strftime('%H:%M') == time
        if _group_calendar[key].get('enable', False) and flag:
            bot = nonebot.get_bot()
            result = await Event(_group_calendar[key]).send_daily_async(2)
            await bot.send_group_msg(group_id = key, message = result)