import os
import aiohttp
import asyncio
import datetime
import json
import traceback

from .base import *

def format_number(number: int) -> str:
    if number == 0:
        return '0'
    num_str = ''
    if number > 100000000: #亿
        yi = number // 100000000
        number %= 100000000
        if yi != 0:
            num_str += f'{yi}亿'
    if number > 10000:
        wan = number // 10000
        number %= 10000
        if wan != 0:
            num_str += f'{wan}万'
    if number != 0:
        num_str += f'{number}'
    return num_str

#格式化出刀记录
def format_challenge_report(challenge_list: list):
    msg = "新增出刀记录:"
    for item in challenge_list:
        dt = datetime.datetime.fromtimestamp(item['datetime'])
        msg += f"\n{dt.strftime('%Y/%m/%d %H:%M:%S')} "
        msg += f"{item['lap_num']}周目 "
        msg += f"{item['boss']+1}王\n"
        msg += f"{item['name']} "
        msg += f"伤害:{format_number(item['damage'])} "
        msg += f"得分:{format_number(item['score'])} "
        if item['kill'] == 1:
            msg += "尾刀"
        if item['reimburse'] == 1:
            msg += "补偿刀"
    return msg

#总表
async def get_collect_report(group_id: str) -> (int, str):
    group_id = str(group_id)
    msg = ""
    data = await query_data(group_id, "collect-report")
    if 'code' not in data: #网络错误
        return '网络异常'
    if data['code'] != 0: #cookie错误
        return 'cookie无效'
    if 'data' not in data: #数据异常
        return '数据异常'
    data = data['data']

    msg = f"公会:{data['clan']['name']}\n"
    msg += f"排名:{data['clan']['last_ranking']}\n"
    msg += "出刀情况:"
    for member in data['data']:
        msg += f"\n昵称:{member['username']} "
        msg += f"出刀:{member['number']} "
        msg += f"伤害:{format_number(member['damage'])} " 
        msg += f"占比:{member['rate']} "
        msg += f"得分:{format_number(member['score'])}"
    return msg

#日表
async def get_day_report(group_id: str, day: int = 0) -> (int, str):
    msg = ''
    day_str = get_daystr_from_daylist(group_id, day)
    if not day_str:
        return '无数据'
    data = await query_data(group_id, "day_report", day_str)
    if 'code' not in data: #网络错误
        return '网络异常'
    if data['code'] != 0: #cookie错误
        return 'cookie无效'
    if 'data' not in data: #数据异常
        return '数据异常'
    data = data['data']

    msg += f"{day_str}的出刀情况:"
    for member in data:
        msg += f"\n{member['name']} "
        msg += f"出刀:{member['number']} "
        msg += f"伤害:{format_number(member['damage'])} "
        msg += f"得分:{format_number(member['score'])}"
    return msg
    
#boss表
async def get_boss_report(group_id: str, boss: int = 0) -> (int, str):
    group_id = str(group_id)
    if boss >= len(boss_challenge_list[group_id]):
        return '序号超出范围'
    challenges = boss_challenge_list[group_id][boss]
    if len(challenges) == 0:
        return '无记录'
    msg = ''
    boss_name = ''
    try:
        boss_name = clanbattle_info[group_id]['boss_list'][boss]['boss_name']
    except:
        boss_name = f'{boss + 1}王'
    msg += f"{boss_name}的出刀记录:"
    for item in challenges:
        dt = datetime.datetime.fromtimestamp(item['datetime'])
        msg += f"\n时间:{dt.strftime('%Y/%m/%d %H:%M:%S')} "
        msg += f"昵称:{item['name']} "
        msg += f"伤害:"
        damage = item['damage']
        if damage > 10000:
            msg += f"{damage // 10000}万"
        msg += f"{damage % 10000} "
        msg += f"得分:{format_number(item['score'])} "
        if item['kill'] == 1:
            msg += "尾刀"
        if item['reimburse'] == 1:
            msg += "补偿刀"
    return msg

#日出刀
async def get_day_challenge_report(group_id: str, day: int = 0) -> (int, str):
    day_str = get_daystr_from_daylist(group_id, day)
    if not day_str:
        return '无数据'
    today = datetime.datetime(*map(int, day_str.split('-')))
    today = today.replace(hour=5, minute=0, second=0, microsecond=0) #当天5点
    tomorrow = today + datetime.timedelta(days=1)

    msg = f"{today.strftime('%Y/%m/%d')}的出刀记录:"
    for item in all_challenge_list[group_id]:
        dt = datetime.datetime.fromtimestamp(item['datetime'])
        if dt >= today and dt < tomorrow:
            msg += f"\n时间:{dt.strftime('%Y/%m/%d %H:%M:%S')} "
            msg += f"昵称:{item['name']} "
            msg += f"伤害:"
            damage = item['damage']
            if damage > 10000:
                msg += f"{damage // 10000}万"
            msg += f"{damage % 10000} "
            msg += f"得分:{format_number(item['score'])} "
            if item['kill'] == 1:
                msg += "尾刀"
            if item['reimburse'] == 1:
                msg += "补偿刀"
    return msg

#个人出刀
async def get_member_challenge_report(group_id: str, name: str) -> (int, str):
    msg = f"{name}的出刀记录:"
    for item in all_challenge_list[group_id]:
        if item['name'] == name:
            dt = datetime.datetime.fromtimestamp(item['datetime'])
            msg += f"\n时间:{dt.strftime('%Y/%m/%d %H:%M:%S')} "
            msg += f"昵称:{item['name']} "
            msg += f"伤害:"
            damage = item['damage']
            if damage > 10000:
                msg += f"{damage // 10000}万"
            msg += f"{damage % 10000} "
            msg += f"得分:{format_number(item['score'])} "
            if item['kill'] == 1:
                msg += "尾刀"
            if item['reimburse'] == 1:
                msg += "补偿刀"
    return msg

#boss状态
def get_boss_state_report(group_id: str) -> (int, str):
    group_id = str(group_id)
    msg = ""
    boss_info = {}
    try:
        boss_info = clanbattle_info[group_id]['boss_info']
        msg = "boss状态:"
        msg += f"\n{boss_info['lap_num']}周目 {boss_info['name']}"
        msg += f"\n{format_number(boss_info['current_life'])} / {format_number(boss_info['total_life'])} "
        msg += f"({boss_info['current_life']/boss_info['total_life']*100:.2f}%)"
    except:
        msg = "无数据"
    return msg
