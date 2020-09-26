import os
import aiohttp
import asyncio
import datetime
import json
import hoshino
import traceback
import re
from hoshino import Service, priv 
from hoshino.typing import CQEvent
from .base import *
from .info import *
from .yobot import *

HELP_MSG = 'clanbattle_info\n公会战信息管理系统\n指令前缀:cbi\n指令表:帮助,总表,日总表,日出刀表,boss出刀表,boss状态,状态,检查成员,绑定,解除绑定,查看绑定,绑定未知成员,解除绑定未知成员,继续报刀,暂停报刀,重置报刀进度,重置推送进度,初始化\n详细说明见项目文档: https://github.com/zyujs/clanbattle_info'

process_lock = {}

sv = Service('clanbattle_info', bundle='pcr查询', help_= HELP_MSG)

@sv.on_prefix('cbi')
async def cbi(bot, ev: CQEvent):
    msg = ''
    user_id = ev.user_id
    target_id = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            target_id = int(m.data['qq'])
    group_id = str(ev.group_id)
    args = ev.message.extract_plain_text().split()
    is_admin = priv.check_priv(ev, priv.ADMIN)

    if group_id not in group_config or group_config[group_id]['state'] == 'failed':
        if len(args) > 0 and args[0] == '初始化':
            if await init_group(group_id) != 0:
                await bot.send(ev, f'数据初始化失败:{group_config[group_id]["info"]}')
                return
            else:
                await bot.send(ev, '群数据初始化成功')
                return
        else:
            await bot.send(ev, f'群组数据未初始化:请使用"cbi 初始化"命令初始化数据')
        return
    if group_id not in group_config or group_config[group_id]['state'] == 'uninited':
        await bot.send(ev, '正在初始化群组数据')
        if await init_group(group_id) != 0:
            await bot.send(ev, f'数据初始化失败:{group_config[group_id]["info"]}')
            return

    #不需要权限的部分
    if len(args) == 0:
        msg = HELP_MSG
    elif args[0] == '帮助':
        msg = HELP_MSG
    elif args[0] == '总表':
        msg = await get_collect_report(group_id)
    elif args[0] == '日总表':
        day = 0
        if len(args) >= 2 and args[1].isdigit():
            day = int(args[1]) - 1
        if day < 0:
            day = 0
        msg = await get_day_report(group_id, day)
    elif args[0] == '日出刀表':
        day = 0
        if len(args) >= 2 and args[1].isdigit():
            day = int(args[1]) - 1
        if day < 0:
            day = 0
        msg = await get_day_challenge_report(group_id, day)
    elif args[0] == 'boss出刀表':
        boss = 0
        if len(args) >= 2 and args[1].isdigit():
            boss = int(args[1])
        if boss > 0:
            boss -= 1
        msg = await get_boss_report(group_id, boss)
    elif args[0] == '查看绑定':
            msg = get_bind_msg(group_id)
    elif args[0] == '状态':
        msg = get_state_msg(group_id)
    elif args[0] == '继续报刀':
        set_yobot_state(group_id, False)
        await bot.send(ev, '已继续')
        await group_process(bot, group_id)
        return
    elif args[0] == 'boss状态':
        msg = get_boss_state_report(group_id)
    #需要权限的部分
    elif args[0] == '初始化':
        if is_admin:
            if await init_group(group_id) != 0:
                msg = f'数据初始化失败:{group_config[group_id]["info"]}'
            else:
                msg = '群数据初始化成功'
        else:
            msg = '权限不足'
    elif args[0] == '绑定':
        name = '?'
        if len(args) >= 2:
            name = args[1]
            names = re.findall(r"\[(.+?)\]",ev.message.extract_plain_text())
            if len(names) > 0:
                name = names[0]
        if len(args) < 2: #最小参数 绑定 昵称
            msg = '参数错误'
        elif target_id == 0: #绑定自己 或者bot
            if len(args) >= 3 and args[-1] == 'bot': #绑定 昵称 bot
                if is_admin:
                    add_bind(group_id, name, ev.self_id)
                    msg = f'已绑定 {name}:{ev.self_id}'
                else:
                    msg = '权限不足'
            else: #绑定 昵称
                add_bind(group_id, name, user_id)
                msg = f'已绑定 {name}:{user_id}'
        else: #绑定别人
            if is_admin:
                add_bind(group_id, name, target_id)
                msg = f'已绑定 {name}:{target_id}'
            else:
                msg = '权限不足'
    elif args[0] == '解除绑定':
        name = '?'
        if len(args) >= 2:
            name = args[1]
            names = re.findall(r"\[(.+?)\]",ev.message.extract_plain_text())
            if len(names) > 0:
                name = names[0]
        if len(args) < 2:
            msg = '参数错误'
        elif not is_admin:
            msg = '权限不足'
        else:
            remove_bind(group_id, name)
            msg = f'已解除绑定 {name}'
    elif args[0] == '绑定未知成员':
        if not is_admin:
            msg = '权限不足'
        elif len(args) == 1 and target_id == 0:
            add_bind(group_id, magic_name, user_id)
            msg = f'已将全部未知成员绑定至 {user_id}'
        elif len(args) >= 2 and args[1] == 'bot': #bot
            add_bind(group_id, magic_name, ev.self_id)
            msg = f'已将全部未知成员绑定至 {ev.self_id}'
        else:
            msg = '指令错误'
    elif args[0] == '解除绑定未知成员':
        if not is_admin:
            msg = '权限不足'
        else:
            remove_bind(group_id, magic_name)
            msg = f'已解除对未知成员的绑定'
    elif args[0] == '暂停报刀':
        if not is_admin:
            msg = '权限不足'
        else:
            set_yobot_state(group_id, True)
            msg = '已暂停'
    elif args[0] == '重置推送进度':
        if not is_admin:
            msg = '权限不足'
        else:
            group_data[group_id]['index'] = 0
            msg = '已重置'
    elif args[0] == '重置报刀进度':
        if not is_admin:
            msg = '权限不足'
        else:
            group_data[group_id]['yobot_index'] = 0
            msg = '已重置'
    elif args[0] == '检查成员':
        if not is_admin:
            msg = '权限不足'
        else:
            msg = await get_unknown_members_report(group_id)
    else:
        msg = '指令错误,请阅读帮助文档.\n'

    await bot.send(ev, msg)

#状态更新 出刀推送 自动报刀
#必须使用线程池调用这个过程,以避免被报刀量较大的群卡住刷新数据过程
async def group_process(bot, group_id: str):
    if group_id not in process_lock:
        process_lock[group_id] = asyncio.Lock()
    if process_lock[group_id].locked():
        return
    await process_lock[group_id].acquire()
    try:
        ret = await update_clanbattle_data(group_id)
        if ret == 2:
            msg = f"[clanbattle_info]\n数据更新出现异常:{group_config[group_id]['info']}\n数据推送服务已挂起, 请排除故障后使用'cbi 初始化'命令重新启动数据更新服务."
            await bot.send_group_msg(group_id=int(group_id), message = msg)
        elif ret == 0:
            #出刀推送
            if group_config[group_id]['push_challenge']:
                result = get_new_challenges(group_id)
                if len(result) > 0:
                    msg = format_challenge_report(result)
                    await bot.send_group_msg(group_id=int(group_id), message = msg)
            #自动报刀
            if is_auto_report_enable(group_id):
                await report_process(bot, group_id)
    except:
        traceback.print_exc()
    process_lock[group_id].release()
        
#每个整5分钟的+30s~+3m30s范围执行任务
@sv.scheduled_job('cron',minute='2,7,12,17,22,27,32,37,42,47,52,57', jitter=90)
async def job():
    bot = hoshino.get_bot()
    updated = await check_update()

    available_group = {}
    bot_group_list = await bot.get_group_list()
    for item in bot_group_list:
        available_group[int(item['group_id'])] = True

    glist = get_group_list()
    tasks = []
    for group_id in glist:
        if int(group_id) in available_group:
            if updated:
                await bot.send_group_msg(group_id=int(group_id), message = 'clanbattle_info插件检测到新的提交记录,请及时更新.')
            tasks.append(asyncio.ensure_future(group_process(bot, str(group_id))))
    for task in asyncio.as_completed(tasks):
        await task

def init():
    glist = get_group_list()
    for group_id in glist:
        preinit_group(group_id)

init()
