import datetime
import aiohttp
import asyncio
import traceback
import math
import datetime
import nonebot
import hoshino
from .base import *

__all__ = [
    'is_auto_report_enable',
    'format_yobot_report_message',
    'set_yobot_state',
    'get_embedded_yobot_ClanBattle_instance',
    'report_process',
    'get_unknown_members_report',
    ]

### standalone 模式

async def query_yobot_data(api_url: str) -> (int, dict or str):
    data = None
    for _ in range(5):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    break
        except:
            traceback.print_exc()
    if not data:
        return 1, 'YobotAPI访问异常'
    if 'members' not in data or 'challenges' not in data:
        return 1, 'YobotAPI数据异常'
    return 0, data

#格式化yobot报刀信息
def format_yobot_report_message(challenge: dict):
    msg = ''
    if challenge['kill'] == 1:
        msg += '尾刀 '
    else:
        msg += f'报刀 {challenge["damage"]} '
    dt = datetime.datetime.fromtimestamp(challenge['datetime'])
    msg += f'[CQ:at,qq={challenge["qqid"]}] '
    if get_pcr_days_from(dt) > 0:
        msg += '昨日 '
    return msg

### 缝合模式功能

#获取插件版yobot的ClanBattle实例
def get_embedded_yobot_ClanBattle_instance():
    plugins = nonebot.get_loaded_plugins()
    for plugin in plugins:
        m = str(plugin.module)
        m = m.replace('\\\\', '/')
        m = m.replace('\\', '/')
        if 'modules/yobot/yobot/__init__.py' in m:
            passive_list = []
            try:
                passive_list = plugin.module.src.client.nonebot_plugin.bot.plug_passive
            except:
                continue
            for module in passive_list:
                if type(module).__name__ == 'ClanBattle':
                    return module
    return None

#插件版yobot报刀
def embedded_yobot_add_challenge(group_id: str, challenge):
    msg = ''
    clanbattle = get_embedded_yobot_ClanBattle_instance()
    if not clanbattle:
        msg = '无法获取ClanBattle实例,请检查yobot部署或切换至yobot_standalone模式.'
        return 1, msg
    defeat = False
    if challenge['kill'] == 1:
        defeat = True
    previous_day = False
    dt = datetime.datetime.fromtimestamp(challenge['datetime'])
    if get_pcr_days_from(dt) > 0:
        previous_day = True
    try:
        result = clanbattle.challenge(int(group_id), challenge['qqid'], defeat, challenge['damage'], None, previous_day=previous_day)
        msg = 'yobot新增出刀记录:\n' + str(result)
    except Exception as e:
        msg = 'yobott添加出刀记录失败:\n' + str(e)
        return 1, msg
    return 0, msg

### 通用功能

def is_auto_report_enable(group_id: str):
    if group_id not in group_config:
        return False
    if 'report_mode' not in group_config[group_id]:
        return False
    if group_config[group_id]['report_mode'] == 'yobot_standalone': #独立模式 发报刀消息
        return True
    elif group_config[group_id]['report_mode'] == 'yobot_embedded': #嵌入模式 直接调用函数
        return True
    return False

#格式化出刀记录
def format_challenge(challenge: dict):
    if len(challenge) == 0:
        return '空\n'
    msg = ''
    dt = datetime.datetime.fromtimestamp(challenge['datetime'])
    msg += f"{dt.strftime('%Y/%m/%d %H:%M:%S')} "
    msg += f"{challenge['name']}({challenge['qqid']}) "
    msg += f"伤害:{challenge['damage']} "
    msg += f"{challenge['lap_num']}周目 "
    msg += f"{challenge['boss']+1}王 "
    if challenge['kill'] == 1:
        msg += "尾刀"
    if challenge['reimburse'] == 1:
        msg += "补偿刀"
    msg += "\n"
    return msg

#格式化出刀记录
def format_yobot_challenge(challenge: dict):
    if len(challenge) == 0:
        return '空\n'
    msg = ''
    dt = datetime.datetime.fromtimestamp(challenge['challenge_time'])
    msg += f"{dt.strftime('%Y/%m/%d %H:%M:%S')} "
    msg += f"QQ:{challenge['qqid']} "
    msg += f"伤害:{challenge['damage']} "
    msg += f"{challenge['cycle']}周目 "
    msg += f"{challenge['boss_num']}王"
    if challenge['health_ramain'] == 0:
        msg += "尾刀"
    if challenge['is_continue']:
        msg += "补偿刀"
    msg += "\n"
    return msg

def check_challenge_equal(challenge: dict, yobot_challenge: dict):
    if challenge['qqid'] != yobot_challenge['qqid']:
        return False
    if challenge['lap_num'] != yobot_challenge['cycle']:
        return False
    if challenge['boss'] + 1 != yobot_challenge['boss_num']:
        return False
    if abs(challenge['damage'] - yobot_challenge['damage']) < 5: #忽略5以内偏差,避免尾数问题
        return True
    if challenge['kill'] == 1 and yobot_challenge['health_ramain'] == 0 \
        and abs(challenge['damage'] - yobot_challenge['damage']) < 10000:   #尾刀容许偏差1w
        return True
    return False

#设置报刀状态
def set_yobot_state(group_id:str, pause:bool):
    group_id = str(group_id)
    if group_id in group_data:
        group_data[group_id]['report_pause'] = pause
        save_group_data(group_id)

#获取yobot最后一条出刀记录
async def get_yobot_challenges(group_id):
    if group_id not in group_data or group_id not in group_config:
        return 1, 'get_yobot_challenges: 配置异常'
    yobot_challenges = []

    if group_config[group_id]['report_mode'] == 'yobot_standalone': #独立模式 发报刀消息
        ret, data = await query_yobot_data(group_config[group_id]['yobot_api'])
        if ret != 0:
            return 1, 'get_yobot_challenges:' + data
        yobot_challenges = data['challenges']
    elif group_config[group_id]['report_mode'] == 'yobot_embedded': #嵌入模式 直接调用函数
        clanbattle = get_embedded_yobot_ClanBattle_instance()
        if not clanbattle:
            return 1, 'get_yobot_challenges: 无法获取ClanBattle实例'
        yobot_challenges = clanbattle.get_report(group_id, None, None, None)

    return 0, yobot_challenges

#等待yobot同步当前出刀记录
#ret: 0 成功 1 出错 2 超时
# 由于yobot内部get_report有时间缓存机制, 获取到最新记录最多要等待10秒
async def wait_yobot_sync(group_id: str, challenge: dict):
    group_id = str(group_id)
    for _ in range(10):
        await asyncio.sleep(3)
        ret, yobot_challenges = await get_yobot_challenges(group_id)
        if ret != 0:
            return 1, 'wait_for_challenge_sync:' + yobot_challenges
        if len(yobot_challenges) == 0:
            continue
        #对比本条记录和Yobot最新记录的qq,伤害,boss,周目,一致则认为同步成功
        #对于尾刀,允许一定的误差(暂定1w内)
        for yobot_challenge in yobot_challenges:
            if check_challenge_equal(challenge, yobot_challenge):
                group_data[group_id]['yobot_index'] = challenge['index']
                save_group_data(group_id)
                return 0, 'ok'

    yobot_challenge = {}
    if len(yobot_challenges) > 0:
        yobot_challenge = yobot_challenges[-1]
    msg = f'最新上报记录匹配失败,请手动修正出刀数据.\n本次上报出刀数据:\n{format_challenge(challenge)}yobot最近出刀数据:\n{format_yobot_challenge(yobot_challenge)}'
    return 2, msg

async def generate_name2qq(group_id: str, yobot_members = None):
    name2qq = {}
    yobot_members = []
    if not yobot_members:
        #从yobot获取成员表
        if group_config[group_id]['report_mode'] == 'yobot_standalone':
            ret, data = await query_yobot_data(group_config[group_id]['yobot_api'])
            if ret != 0:
                return 1, data
            if 'members' in data:
                yobot_members = data['members']
        elif group_config[group_id]['report_mode'] == 'yobot_embedded':
            clanbattle = get_embedded_yobot_ClanBattle_instance()
            if not clanbattle:
                return 1, '无法获取ClanBattle实例,请检查yobot部署情况或切换至yobot_standalone模式.'
            yobot_members = clanbattle.get_member_list(int(group_id))
        else:
            return 1, '自动报刀功能未启用'

    #优先级: 插件本地members -> yobot members -> 群成员列表
    #生成昵称-QQ对应表 
    for (name, qq) in group_data[group_id]['members'].items():
        name2qq[name] = qq
    for item in yobot_members:
        if item['nickname'] not in name2qq:
            name2qq[item['nickname']] = item['qqid']

    bot = hoshino.get_bot()
    mlist = await bot.get_group_member_list(group_id=int(group_id))
    for m in mlist:
        name = m['card'] or m['nickname']
        if name not in name2qq:
            name2qq[name] =  m['user_id']
    return 0, name2qq

#获取未知成员报告
async def get_unknown_members_report(group_id: str) -> str:
    group_id = str(group_id)
    msg = ""
    unknown_list = {}

    ret, name2qq = await generate_name2qq(group_id)
    if ret != 0:
        return name2qq

    data = await query_data(group_id, "collect-report")
    if 'code' not in data: #网络错误
        return '网络异常'
    if data['code'] != 0: #cookie错误
        return 'cookie无效'
    if 'data' not in data: #数据异常
        return '数据异常'
    data = data['data']['data']
    for item in data:
        if item['username'] not in name2qq:
            unknown_list[item['username']] = True
    if len(unknown_list) > 0:
        name_str = ''
        for name in unknown_list:
            name_str += f'[{name}] '
        msg = f'找不到以下游戏成员对应的QQ号码:\n{name_str}'
        if magic_name in group_data[group_id]['members']:
            msg += f"\n上述成员的出刀记录将指定给{group_data[group_id]['members'][magic_name]}"
        return msg
    return '公会成员昵称与QQ全部对应'


#检查yobot记录 如果同步成功 返回出刀表
async def check_yobot(group_id: str) -> (int, list or str):
    group_id = str(group_id)
    if group_id not in group_data or group_id not in group_config:
        return 1, 'check_yobot: 群组配置异常'
    if group_data[group_id]['report_pause']: #功能关闭或者停
        return 0, []
    if group_id not in all_challenge_list or len(all_challenge_list[group_id]) == 0: #游戏记录为空
        return 0, []
    if len(all_challenge_list[group_id]) <= group_data[group_id]['yobot_index']: #已经报刀至最新记录
        return 0, []

    yobot_members = []
    yobot_challenges = []
    if group_config[group_id]['report_mode'] == 'yobot_standalone':
        ret, data = await query_yobot_data(group_config[group_id]['yobot_api'])
        if ret != 0:
            return 1, data
        if 'members' in data:
            yobot_members = data['members']
        if 'challenges' in data:
            yobot_challenges = data['challenges']
    elif group_config[group_id]['report_mode'] == 'yobot_embedded':
        clanbattle = get_embedded_yobot_ClanBattle_instance()
        if not clanbattle:
            return 1, '无法获取ClanBattle实例,请检查yobot部署情况或切换至yobot_standalone模式.'
        yobot_members = clanbattle.get_battle_member_list(int(group_id), None)
        yobot_challenges = clanbattle.get_report(group_id, None, None, None)
    
    ret, name2qq = await generate_name2qq(group_id, yobot_members)
    if ret != 0:
        return 1, name2qq

    #先检查昵称是否有对应qq
    unknown_name = {}
    for i in range(len(all_challenge_list[group_id])):
        challenge = all_challenge_list[group_id][i]
        if challenge['name'] not in name2qq:
            unknown_name[challenge['name']] = True
    if magic_name not in group_data[group_id]['members'] and len(unknown_name) > 0:
        name_str = ''
        for name in unknown_name:
            name_str += f'[{name}] '
        msg = f'找不到以下游戏昵称对应的yobot会员数据,请检查yobot会员设置或使用"cbi 绑定"命令手动绑定.\n{name_str}'
        return 1, msg

    #先匹配yobot出刀表最后一条 如果能匹配到说明yobot的记录更新 直接返回空
    last_challenge = all_challenge_list[group_id][-1]
    if last_challenge['name'] in name2qq:
        last_challenge['qqid'] = name2qq[last_challenge['name']]
    else:
        last_challenge['qqid'] = name2qq[magic_name]
    for i in range(group_data[group_id]['yobot_index'], len(yobot_challenges)):
        if check_challenge_equal(last_challenge, yobot_challenges[i]):
            return 0, []

    index = -1
    yobot_index = len(yobot_challenges) - 1
    #要处理yobot最新记录是掉刀记录的情况 考虑连续多条0伤害掉刀记录的极端情况 同时还要考虑确实有0伤害甜心刀游戏记录
    while index < 0 and yobot_index >=0:
        #查找yobot最新一条记录在总表中的位置
        for i in range(len(all_challenge_list[group_id])):
            challenge = all_challenge_list[group_id][i]
            if challenge['name'] in name2qq:
                challenge['qqid'] = name2qq[challenge['name']]
            else:
                challenge['qqid'] = name2qq[magic_name]
            if check_challenge_equal(challenge, yobot_challenges[yobot_index]):
                index = i
                break
        if yobot_challenges[yobot_index]['damage'] != 0:
            break
        yobot_index -= 1
    #没有匹配记录且yobot记录不为空
    if index < 0 and yobot_index >= 0:
        yobot_challenge = {}
        if yobot_index >= 0 and yobot_index < len(yobot_challenges):
            yobot_challenge = yobot_challenges[yobot_index]
        msg = f"未找到与yobot最新出刀记录匹配的游戏数据,请检查yobot伤害记录及角色名是否与游戏记录一致.\nyobot最近出刀数据:\n{format_yobot_challenge(yobot_challenge)}游戏最新出刀数据:\n{format_challenge(all_challenge_list[group_id][-1])}"
        return 1, msg
    
    #找到对应数据
    new_challenges = []
    for i in range(index+1, len(all_challenge_list[group_id])):
        item = all_challenge_list[group_id][i]

        dt = datetime.datetime.fromtimestamp(item['datetime'])
        if get_pcr_days_from(dt) > 1 and not group_config[group_id]['debug']:
            msg = f"本条出刀记录距今已超过1天,无法上报至yobot.\n{dt.strftime('%Y/%m/%d %H:%M:%S')} {item['name']} 伤害:{item['damage']} {item['lap_num']}周目 {item['boss']+1}王"
            return 1, msg
        if item['name'] in name2qq:
            item['qqid'] = name2qq[item['name']]
        else:
            item['qqid'] = name2qq[magic_name]
        item['index'] = i
        new_challenges.append(item)
    return 0, new_challenges


async def report_process(bot, group_id: str):
    group_id = str(group_id)
    if group_id not in group_config:
        return
    if group_config[group_id]['state'] != 'run':
        return
    if group_data[group_id]['report_pause']:
        return
    if not is_auto_report_enable(group_id):
        return

    ret, result = await check_yobot(group_id)
    if ret != 0:
        group_data[group_id]['report_pause'] = True
        await send_group_msg(bot, group_id, result)
        return

    for item in result:
        if group_data[group_id]['report_pause']: #暂停
            return
        if group_config[group_id]['report_mode'] == 'yobot_standalone': #独立模式 发报刀消息
            result = format_yobot_report_message(item)
            await send_group_msg(bot, group_id, result)
        elif group_config[group_id]['report_mode'] == 'yobot_embedded': #嵌入模式 直接调用函数
            ret, result = embedded_yobot_add_challenge(group_id, item)
            await send_group_msg(bot, group_id, result)
            if ret != 0:
                group_data[group_id]['report_pause'] = True
                return
        else:
            return

        ret, result = await wait_yobot_sync(group_id, item)
        if ret != 0: #同步失败
            group_data[group_id]['report_pause'] = True
            await send_group_msg(bot, group_id, result)
            return

