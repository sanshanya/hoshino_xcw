import os
import aiohttp
import datetime
import json
import hoshino
import re
from hoshino import Service, priv 
from hoshino.typing import CQEvent

api_search = 'https://tools-wiki.biligame.com/pcr/getTableInfo?type=search&search={}&page=0'
api_subsection = 'https://tools-wiki.biligame.com/pcr/getTableInfo?type=subsection'

lmt = hoshino.util.FreqLimiter(10)

cycle_data = {
    'cycle_mode': 'days',
    'cycle_days': 28,
    'base_date': datetime.date(2020, 7, 28),  #从巨蟹座开始计算
    'base_month': 5,
    'battle_days': 6
}

sv = Service('clanbattle_rank', bundle='pcr查询', help_= '查询排名 公会名 [会长名] : 查询指定公会排名\n查询分段 : 查询分段信息\n查询关注 : 查询关注的公会信息\n添加关注 公会名 [会长名] : (需要管理员权限)将指定公会加入关注列表,如有重名需要附加会长名\n清空关注 : (需要管理员权限)清空关注列表')
sv_push = Service('clanbattle_rank_push', bundle='pcr查询', help_= '关注公会信息每日自动推送')

boss_data = {
    "hp": [
        [6000000, 8000000, 10000000, 12000000, 20000000],
        [6000000, 8000000, 10000000, 12000000, 20000000],
    ],
    "rate": [
        [1.0, 1.0, 1.3, 1.3, 1.5],  #1
        [1.3, 1.3, 1.8, 1.8, 2.0]  #2-10
    ],
    "step": [0, 1]
}

def get_days_from_battle_start():
    today = datetime.date.today()
    return (today - cycle_data['base_date']).days % cycle_data['cycle_days']

def load_group_config(group_id):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    if not os.path.exists(config_file):
        return {}  # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        sv.logger.error(f'Error: {e}')
        return {}

def save_group_config(group_id, config):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    try:
        with open(config_file, 'w', encoding='utf8') as f:
            json.dump(config , f, ensure_ascii=False, indent=2)
    except Exception as e:
        sv.logger.error(f'Error: {e}')

def delete_group_config(group_id):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    if os.path.exists(config_file):
        try:
            os.remove(config_file)
        except Exception as e:
            sv.logger.error(f'Error: {e}')

#从配置文件夹生成群列表
def get_group_list():
    group_list = []
    path = os.path.join(os.path.dirname(__file__), 'data')
    list = os.listdir(path)
    for fn in list:
        group = fn.split('.')[0]
        if group.isdigit():
            group_list.append(int(group))
    return group_list
        

def add_follow_clan(group_id, clan_name, leader_name):
    config = load_group_config(group_id)
    config[clan_name] = leader_name
    save_group_config(group_id, config)

def get_boss_process(score):
    lap = 0 #周目
    step = 0 #阶段 0-3
    current_boss = 0    #当前boss 0-4
    remain_score = score    #剩余分数

    boss_hp = boss_data["hp"]
    boss_rate = boss_data["rate"]
    boss_step = boss_data["step"]

    while True:
        step = 0
        for i in range(0, len(boss_step)):
            if lap >= boss_step[i]:
                step = i
        current_boss_score = boss_hp[step][current_boss] * boss_rate[step][current_boss]
        if current_boss_score > remain_score:
            break
        remain_score -= current_boss_score
        current_boss += 1
        if current_boss > 4:
            current_boss = 0
            lap += 1
    remain_hp = int(boss_hp[step][current_boss] - remain_score/boss_rate[step][current_boss])
    boss_hp = boss_hp[step][current_boss]
    return f'{lap+1}周目{current_boss+1}王 [{remain_hp // 10000}万/{boss_hp // 10000}万] {round(remain_hp * 100/ boss_hp, 2)}%'

def format_clan_info(clan_info):
    msg = f'公会:{clan_info["clan_name"]}\n' \
        + f'会长:{clan_info["leader_name"]}\n' \
        + f'排名:{clan_info["rank"]}\n' \
        + f'分数:{clan_info["damage"]}\n' \
        + f'进度:{get_boss_process(clan_info["damage"])}\n'
    return msg

def format_compact_clan_info(clan_info):
    msg = f'公会:{clan_info["clan_name"]}  ' \
        + f'会长:{clan_info["leader_name"]}  ' \
        + f'排名:{clan_info["rank"]}  ' \
        + f'分数:{clan_info["damage"]}\n'
    return msg

def format_subsection_clan_info(clan_info):
    msg = f'排名:{clan_info["rank"]}  ' \
        + f'分数:{clan_info["damage"]}  '
    if 'clan_name' in clan_info:
        msg += f'公会:{clan_info["clan_name"]}  ' \
        + f'会长:{clan_info["leader_name"]}\n'
    else:
        msg += '公会:-  会长:-\n'
    return msg

#从bilibili获取公会信息列表
async def query_clan_info_biligame(clan_name):
    info_list = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_search.format(clan_name)) as resp:
                info_list = await resp.json(content_type='text/plain')
    except Exception as e:
        hoshino.logger.error(f'clan info response error: {e}')
    return info_list

#从bilibili获取公会信息列表
async def query_subsection_info_biligame():
    info_list = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_subsection) as resp:
                info_list = await resp.json(content_type='text/plain')
    except Exception as e:
        hoshino.logger.error(f'clan info response error: {e}')
    return info_list

#搜索公会并返回结果数组
async def search_clan(clan_name, leader_name = None):
    info_list = await query_clan_info_biligame(clan_name)
    result_list = []
    for info in info_list:
        if leader_name: #指定了会长名
            if info["leader_name"] == leader_name:
                result_list.append(info)
        else:
            result_list.append(info)
    return result_list

async def get_clan_report(clan_name, leader_name):
    clan_list = await search_clan(clan_name, leader_name)
    report = ""
    if len(clan_list) == 0:
        report = "找不到指定公会数据"
    elif len(clan_list) == 1:
        report = format_clan_info(clan_list[0])
    else:   #列出全部结果
        report = "查询到以下结果\n"
        for info in clan_list:
            report += format_compact_clan_info(info)
    return report

async def get_subsection_report():
    clan_list = await query_subsection_info_biligame()
    report = ""
    if len(clan_list) == 0:
        report = "数据获取失败\n"
    else:   #列出全部结果
        report = "分段数据:\n"
        for info in clan_list:
            report += format_subsection_clan_info(info)
    return report

#获取关注公会报告
async def get_follow_clan_report(group_id):
    config = load_group_config(group_id)
    if len(config) == 0:
        return "无关注数据"
    report = "关注的公会排名:\n"
    for clan_name, leader_name in config.items():
        clan_list = await search_clan(clan_name, leader_name)
        if len(clan_list) == 1:
            report += format_compact_clan_info(clan_list[0])
        else:
            report += f"公会:{clan_name}  会长:{leader_name}  未找到数据\n"
    return report

def get_arg_names(arg: str):
    clan_name = None
    leader_name = None

    names = re.findall(r"\[(.+?)\]",arg)
    if len(names) > 0:
        clan_name = names[0]
        if len(names) > 1:
            leader_name = names[1]
    else: #不带[]
        args = arg.split()
        clan_name = args[0]
        if len(args) > 1:
            leader_name = args[1]
    return clan_name, leader_name


@sv.on_fullmatch('查询分段')
async def query_subsection(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.send(ev, f'冷却中, 剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)
    msg = await get_subsection_report()
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(['查询排名', '排名查询'])
async def query_rank(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.send(ev, f'冷却中, 剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)
    clan_name, leader_name = get_arg_names(ev.message.extract_plain_text())
    if not clan_name:
        await bot.send(ev, '参数错误', at_sender=True)
        return
    msg = await get_clan_report(clan_name, leader_name)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix('添加关注')
async def add_follow(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '该操作需要管理员权限', at_sender=True)
        return

    if not lmt.check(uid):
        await bot.send(ev, f'冷却中, 剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)

    clan_name, leader_name = get_arg_names(ev.message.extract_plain_text())
    if not clan_name:
        await bot.send(ev, '参数错误', at_sender=True)
        return
    clan_list = await search_clan(clan_name, leader_name)
    msg = ""
    if len(clan_list) == 0:
        msg = "找不到指定公会"
    elif len(clan_list) == 1:
        info = clan_list[0]
        add_follow_clan(gid, clan_name, info["leader_name"])
        msg = "关注成功\n"
        msg += format_clan_info(info)
    else:   #列出全部结果
        msg = '查询到以下公会\n请使用"关注排名 公会名 会长"命令指定关注的公会\n'
        for info in clan_list:
            msg += format_compact_clan_info(info)
    
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix('删除关注')
async def remove_follow(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '该操作需要管理员权限', at_sender=True)
        return
    clan_name, _ = get_arg_names(ev.message.extract_plain_text())
    if not clan_name:
        await bot.send(ev, '参数错误', at_sender=True)
        return
    msg = ''
    config = load_group_config(gid)
    if clan_name in config:
        config.pop(clan_name)
        save_group_config(gid, config)
        msg = '删除成功'
    else:
        msg = '未关注指定公会'
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('查询关注')
async def query_follow(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    if not lmt.check(uid):
        await bot.send(ev, f'冷却中, 剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)
    msg = await get_follow_clan_report(gid)
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch('清空关注')
async def clear_follow(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '该操作需要管理员权限', at_sender=True)
        return
    if not lmt.check(uid):
        await bot.send(ev, f'冷却中, 剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)
    delete_group_config(gid)
    await bot.send(ev, "关注列表已清空", at_sender=True)

#每日推送
@sv_push.scheduled_job('cron',hour='5',minute='30')
async def clanbattle_rank_push_daily():
    days = get_days_from_battle_start()
    if days >= cycle_data['battle_days']:
        return
    bot = hoshino.get_bot()
    group_list = get_group_list()
    for gid in group_list:
        if days == 0:
            msg = '公会战开始啦!看看这都几点了?还不快起床出刀?'
        else:
            msg = await get_follow_clan_report(gid)
        try:
            await bot.send_group_msg(group_id=int(gid), message = msg)
            hoshino.logger.info(f'群{gid} 推送排名成功')
        except:
            hoshino.logger.info(f'群{gid} 推送排名错误')
        
#最后一天推送 0点之后数据全部木大 所以改到最后一天23点55推送最终数据
@sv_push.scheduled_job('cron',hour='23',minute='55')
async def clanbattle_rank_push_final():
    days = get_days_from_battle_start()
    if days != cycle_data['battle_days'] - 1:
        return
    bot = hoshino.get_bot()
    group_list = get_group_list()
    for gid in group_list:
        msg = '公会战即将结束,各位成员辛苦了!\n祝大家人生有梦,各自精彩!\n'
        msg += await get_follow_clan_report(gid)
        try:
            await bot.send_group_msg(group_id=int(gid), message = msg)
            hoshino.logger.info(f'群{gid} 推送排名成功')
        except:
            hoshino.logger.info(f'群{gid} 推送排名错误')
        