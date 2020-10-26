import os
import aiohttp
import datetime
import json
import asyncio
import threading
import traceback
import math
import nonebot

__all__ = [
    #数据
    'group_config',
    'group_data',
    'boss_challenge_list',
    'all_challenge_list',
    'clanbattle_info',
    'magic_name',

    'preinit_group', 
    'init_group', 
    'get_group_list',
    'update_clanbattle_data', 
    'get_new_challenges',
    'save_group_data',
    'query_data',
    'add_bind',
    'remove_bind',
    'get_bind_msg',
    'get_pcr_days_from',
    'get_state_msg',
    'check_update',
    'send_group_msg',
    'get_daystr_from_daylist',
    'get_clanbattle_report_instance',
    'generate_data_for_clanbattle_report',
    'check_reservation',
    'add_reservation',
    'remove_reservation',
    ]

magic_name = '13c941a144c18a98eb54b493ff0bd279' #魔法昵称,用于将全部未知昵称指定给某个qq, 如有重名建议打死

ext_param = ''
#ext_param = '&battle_id=1'  #指定某一期会战 用于debug
base_api = 'https://www.bigfun.cn/api/feweb?target='
targets = {
    #公会总表
    "collect-report": "gzlj-clan-collect-report/a",
    #工会日表: boss状态 公会等级 日期列表
    "day_report_collect": "gzlj-clan-day-report-collect/a" + ext_param,
    "day_report": "gzlj-clan-day-report/a&date={}&page=1&size=30" + ext_param,  #yyyy-mm-dd
    #boss报表
    "boss_report_collect": "gzlj-clan-boss-report-collect/a" + ext_param, #boss报表
    "boss_report": "gzlj-clan-boss-report/a&boss_id={}&page={}" + ext_param, #boss_id page
}

#群设置
group_config = { }

#群状态
group_data = { }

#出刀数据(分boss 官方数据模式)
boss_challenge_list = { }

#出刀数据总表(不分boss)
all_challenge_list = { }

#公会战信息 不保存
clanbattle_info = {}

update_time = ''

#刷新各boss出刀数据
async def update_challenge_list(group_id: str) -> int:
    #获取第一个需要更新的boss
    boss = 0
    full_update = False
    if group_id in all_challenge_list and len(all_challenge_list[group_id]) > 0:
        challenge = all_challenge_list[group_id][-1]
        boss = challenge['boss']
        if challenge['kill'] == 1:
            boss += 1
            boss %= 5
    else:
        full_update = True

    #第一次运行数据为空,需要创建
    if group_id not in boss_challenge_list:
        boss_challenge_list[group_id] = [[] for i in range(5)]

    changed = False
    boss_count = 0
    while True:
        last_challenge = {} #放上次更新的最后一条出刀数据 如果出刀表为空 就空着
        if len(boss_challenge_list[group_id][boss]) != 0:
            last_challenge = boss_challenge_list[group_id][boss][-1]
        challenges = []
        page = 0
        index = -1
        start = 0
        while True:
            #寻找该boss本地最后一条出刀数据在新获取数据中的位置(index)
            #当前循环没有找到就继续循环拉取下一页,直到找到或者读取完全部记录.
            #没有新出刀记录index = 0, 本地记录为空index=-1
            #这个动作不能在整5分进行,否则bigfun数据刷新会导致出刀数据不连续.
            ret, temp_challenges = await query_boss_data(group_id, boss, page)
            if ret != 0:
                group_config[group_id]['info'] = temp_challenges
                return 1
            challenges += temp_challenges
            for i in range(start, len(challenges)):
                if challenges[i] == last_challenge:
                    index = i
                    break
            page += 1
            start += len(challenges)
            if index != -1 or len(temp_challenges) == 0 or len(temp_challenges) % 25 != 0:
                break
        if index == -1: #没有找到匹配项 重置该boss出刀表
            index = len(challenges)
            boss_challenge_list[group_id][boss] = []
        for item in reversed(challenges[0:index]): #将(0~index-1)的新纪录加入列表
            changed = True
            boss_challenge_list[group_id][boss].append(item)
        boss += 1
        boss %= 5
        boss_count += 1
        #如果该boss最后一条出刀为尾刀,则表示可能会存在下一个boss的新出刀记录,继续更新下一个boss,否则就此结束数据更新.
        if len(challenges) == 0 or challenges[0]['kill'] != 1:
            if not full_update:
                break
        #这里处理恰好5个boss最后一刀都是尾刀的情况,防止死循环
        if boss_count > 5:
            break
    
    #如果boss表有更新 重新生成总表
    if changed:
        all_challenge_list[group_id] = []
        challenges = boss_challenge_list[group_id]
        index = [0 for i in range(5)]
        boss = 0
        while index[boss] < len(challenges[boss]):
            challenge = challenges[boss][index[boss]]
            all_challenge_list[group_id].append(challenge)
            index[boss] += 1
            if challenge['kill'] == 1: #击杀
                boss += 1
                boss %= 5
    return 0
                    
#线程安全的更新出刀数据
update_lock = {}
async def safe_update_challenge_list(group_id: str):
    ret = 0
    if group_id not in group_config:
        return ret
    if group_id not in update_lock:
        update_lock[group_id] = asyncio.Lock()
    await update_lock[group_id].acquire()
    try:
        ret = await update_challenge_list(group_id)
    except Exception as _:
        traceback.print_exc()
    update_lock[group_id].release()
    return ret

#载入群设置
def load_group_config(group_id: str) -> int:
    group_id = str(group_id)
    config_file = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
    config = None
    if not os.path.exists(config_file):
        group_config[group_id]['info'] = '配置文件不存在'
        return 1
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
    except:
        traceback.print_exc()
    if not config or len(config) == 0:
        group_config[group_id]['info'] = '配置文件格式错误'
        return 1
    if not group_id in group_config:
        group_config[group_id] = {}
    #cookie
    if 'cookie' in config:
        text = config['cookie']
        text = text.replace(' ','')
        cookie = {}
        for line in text.split(';'):
            if '=' in line:
                key, value = line.split('=',1)
                cookie[key] = value
        group_config[group_id]['cookie'] = cookie
    else:
        group_config[group_id]['cookie'] = {}
    #推送开关
    if 'push_challenge' in config:
        group_config[group_id]['push_challenge'] = config['push_challenge']
    else:
        group_config[group_id]['push_challenge'] = False
    #yobot报刀
    if 'report_mode' in config:
        group_config[group_id]['report_mode'] = config['report_mode']
    else:
        group_config[group_id]['report_mode'] = 'disable'
    #yobotAPI
    if 'yobot_api' in config:
        group_config[group_id]['yobot_api'] = config['yobot_api']
    else:
        group_config[group_id]['yobot_api'] = False
    #debug
    if 'debug' in config:
        group_config[group_id]['debug'] = config['debug']
    else:
        group_config[group_id]['debug'] = False
    return 0

#从配置文件夹生成群列表
def get_group_list():
    group_list = []
    path = os.path.join(os.path.dirname(__file__), 'config')
    list = os.listdir(path)
    for fn in list:
        group = fn.split('.')[0]
        if group.isdigit():
            group_list.append(str(group))
    return group_list

#刷新boss总表
#有用的信息: boss_list boss列表,在公会战期间不会变化
#这部分信息只需要在初始化时更新一次,或新公会战开始时更新一次
#按目前情况 boss_report_collect 始终可以正常获取,在公会战开始前几天会无缝切换至下一次的boss信息
async def update_clanbattle_info_boss(group_id: str):
    #检查是否需要更新
    if 'boss_update_datetime' in clanbattle_info[group_id]:
        if datetime.datetime.now() < clanbattle_info[group_id]['boss_update_datetime']:
            return 0
    #刷新boss列表 会战星座名
    data = await query_data(group_id, "boss_report_collect")
    if not data or len(data) == 0:
        group_config[group_id]['info'] = 'boss_report_collect接口访问异常'
        return 1
    if not 'data' in data:
        group_config[group_id]['info'] = 'cookie无效'
        return 1
    data = data['data']
    if 'boss_list' in data:
        #boss列表 [{id: "501", boss_name: "双足飞龙"}, {id: "502", boss_name: "野性狮鹫"}, {id: "503", boss_name: "雷电"},…]
        clanbattle_info[group_id]['boss_list'] = data['boss_list']
        clanbattle_info[group_id]['boss_update_datetime'] = get_pcr_tomorrow_datetime()
    #星座名 "狮子座"
    #if 'name' in data:
    #    clanbattle_info[group_id]['name'] = data['name']
    return 0

#刷新日总表
#有用的信息: battle_info 会战信息 day_list 会战日期列表
# day_report_collect 数据在公会战开始前几天会有一段时间空白期, 返回空数据, 需要判断处理
# boss_info需要持续更新
async def update_clanbattle_info_day(group_id: str):
    #检查是否需要更新
    data = await query_data(group_id, "day_report_collect")
    if not data or len(data) == 0:
        group_config[group_id]['info'] = 'day_report_collect接口访问异常'
        return 1
    if not 'data' in data:
        group_config[group_id]['info'] = 'cookie无效'
        return 1
    data = data['data']
    if 'battle_info' in data:
        #会战信息 {id: 1, name: "狮子座"}
        clanbattle_info[group_id]['battle_info'] = data['battle_info']
    else:
        clanbattle_info[group_id]['battle_info'] = {}
    #boss状态 {name: "狂乱魔熊", total_life: 12000000, current_life: 2885013, lap_num: 1}
    if 'boss_info' in data:
        clanbattle_info[group_id]['boss_info'] = data['boss_info']
    else:
        clanbattle_info[group_id]['boss_info'] = {}
    #公会信息 {name: "内鬼连结", last_ranking: -1, last_total_ranking: "B"}
    if 'clan_info' in data:
        clanbattle_info[group_id]['clan_info'] = data['clan_info']
    else:
        clanbattle_info[group_id]['clan_info'] = {}
    #日期列表 ["2020-08-29", "2020-08-28", "2020-08-27", "2020-08-26", "2020-08-25", "2020-08-24"]
    if 'day_list' in data:  #day_list在公会战开始后数小时刷新 直接更新全部日期 降序排列
        clanbattle_info[group_id]['day_list'] = data['day_list']
    else:
        clanbattle_info[group_id]['day_list'] = []
    return 0

#载入群数据
def load_group_data(group_id: str) -> int:
    group_id = str(group_id)
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, encoding='utf8') as f:
                group_data[group_id] = json.load(f)
        except:
            traceback.print_exc()

    if not group_id in group_data:
        group_data[group_id] = {}

    #如果相应数据为空 新建数据
    if 'index' not in group_data[group_id]: #出刀信息推送位置
        group_data[group_id]['index'] = 0
    if 'yobot_index' not in group_data[group_id]: #yobot报刀位置
        group_data[group_id]['yobot_index'] = 0
    if 'members' not in group_data[group_id]:   #游戏名-qq对应表
        group_data[group_id]['members'] = {}
    if 'report_pause' not in group_data[group_id]:   #yobot报刀暂停
        group_data[group_id]['report_pause'] = False
    if 'battle_info' not in group_data[group_id]:
        group_data[group_id]['battle_info'] = {}
    if 'reservation' not in group_data[group_id]:
        group_data[group_id]['reservation'] = {str(i): [] for i in range(5)}
    return 0

#保存群数据
def save_group_data(group_id: str):
    group_id = str(group_id)
    if group_id not in group_data:
        return
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    try:
        with open(config_file, 'w', encoding='utf8') as f:
            json.dump(group_data[group_id], f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

async def query_data(group_id: str, target: str, *ext):
    group_id = str(group_id)
    cookie = {}
    if group_id in group_config:
        cookie = group_config[group_id]['cookie']
    try:
        async with aiohttp.ClientSession(cookies=cookie) as session:
            async with session.get(base_api + targets[target].format(*ext)) as resp:
                return await resp.json(content_type='application/json')
    except:
        traceback.print_exc()
    return None

#获取boss出刀数据
async def query_boss_data(group_id, boss = 0, page = 0):
    challenges = []
    boss_id = 0
    #在会战开始前可以能无法获取boss_list 这种情况直接返回空列表
    try:
        boss_id = clanbattle_info[group_id]['boss_list'][boss]['id']
    except:
        traceback.print_exc()
        return 1, 'query_boss_data: 无法获取boss_id'
    page += 1 #api的page从1开始

    data = await query_data(group_id, "boss_report", boss_id, page)
    if not data or len(data) == 0:
        return 1, 'query_boss_data: api访问失败'
    if not 'data' in data:
        return 1, 'query_boss_data: api数据异常'
    data = data['data']
    for item in data:
        item['boss'] = boss #源数据没有boss序号 额外加入
        challenges.append(item)
    return 0, challenges

#预初始化群组数据
#一个群组在任何操作前必须调用该函数生成基本设置
def preinit_group(group_id: str):
    group_id = str(group_id)
    if group_id not in group_config:
        group_config[group_id] = {}
    if group_id not in group_data:
        group_data[group_id] = {}
    if group_id not in clanbattle_info:
        clanbattle_info[group_id] = {}
    if group_id not in all_challenge_list:
        all_challenge_list[group_id] = {}
    if group_id not in boss_challenge_list:
        boss_challenge_list[group_id] = [{} for i in range(0,5)]
    if 'state' not in group_config[group_id]:
        group_config[group_id]['state'] = 'uninited' #未初始化状态
    if 'info' not in group_config[group_id]:
        group_config[group_id]['info'] = ''

#初始化群数据: 上次boss状态 上次boss和index 载入全部boss出刀记录
async def init_group(group_id: str, internal: bool = False) -> int:
    group_id = str(group_id)
    if group_id not in group_config:
        preinit_group(group_id)
    group_config[group_id]['state'] = 'failed'
    group_config[group_id]['info'] = 'init_group: 未知错误'
    #载入群设置
    if load_group_config(group_id) != 0:
        return 1
    #载入群状态记录
    if load_group_data(group_id) != 0:
        return 1
    #清除出刀数据 以便于数据异常恢复
    clanbattle_info[group_id] = {}
    boss_challenge_list[group_id] = [[] for i in range(5)]
    all_challenge_list[group_id] = []
    #依次从接口获取数据, 某个过程失败就不再继续后续进程
    if await update_clanbattle_info_boss(group_id) != 0 or await update_clanbattle_info_day(group_id) != 0 or await safe_update_challenge_list(group_id) != 0:
        if internal:
            clanbattle_info[group_id]['failed_cnt'] = 1
        else:
            halt_until_tomorrow(group_id)
            return 1
    group_config[group_id]['state'] = 'run'
    return 0

#暂停到明天
def get_pcr_tomorrow_datetime():
    dt = datetime.datetime.now()
    if dt.hour >= 5:
        dt += datetime.timedelta(days=1)
    dt = dt.replace(hour=5, minute=30, second=0, microsecond=0)
    return dt

#暂停到明天
def halt_until_tomorrow(group_id: str):
    dt = get_pcr_tomorrow_datetime()
    clanbattle_info[group_id]['halt_until'] = dt
    group_config[group_id]['state'] = 'halt'

#是否在挂起状态
def is_on_halt(group_id: str) -> bool:
    now = datetime.datetime.now()
    #空闲日直接返回
    if 'halt_until' in clanbattle_info[group_id]:
        if now < clanbattle_info[group_id]['halt_until']:
            return True
    return False

#检查新出刀记录
#返回: 0 更新成功 1 无更新或者无需更新 2 报错
async def update_clanbattle_data(group_id: str) -> int:
    group_id = str(group_id)
    if group_id not in group_config: #没有经过预初始化,表明没有该群的配置
        return 1
    if group_config[group_id]['state'] == 'halt':
        if is_on_halt(group_id): #在挂起期内
            return 1
        else:
            ret = await init_group(group_id, True)
            if ret != 0:
                return 1
    elif group_config[group_id]['state'] == 'failed':
        return 1
    elif group_config[group_id]['state'] == 'uninited': #未初始化
        if await init_group(group_id, True) != 0:
            return 1
    elif group_config[group_id]['state'] == 'run': #正常
        pass
    else: #未知状态
        return 1

    #初始化错误计数
    if 'failed_cnt' not in clanbattle_info[group_id]:
        clanbattle_info[group_id]['failed_cnt'] = 0

    #在run状态下出错, 需要上层发送群消息报告异常
    if await update_clanbattle_info_boss(group_id) != 0 or await update_clanbattle_info_day(group_id) != 0:
        clanbattle_info[group_id]['failed_cnt'] += 1
        if clanbattle_info[group_id]['failed_cnt'] > 12: #连续炸一个小时就挂起
            halt_until_tomorrow(group_id)
            return 2
        else:
            return 1
    else:
        clanbattle_info[group_id]['failed_cnt'] = 0

    #如果day_list为空,表明现在是会战开始前的几天
    #因为会战开始当天前几个小时很可能一直都是空的,所以不能Halt,只能直接返回.
    if 'day_list' not in clanbattle_info[group_id] or len(clanbattle_info[group_id]['day_list']) == 0:
        return 1

    if clanbattle_info[group_id]['battle_info'] != group_data[group_id]['battle_info']: #会战信息改变
        #新的公会战开启 重置各项数据
        #await update_clanbattle_info_boss(group_id)
        boss_challenge_list[group_id] = [[] for i in range(5)]
        all_challenge_list[group_id] = []
        group_data[group_id]['index'] = 0
        group_data[group_id]['yobot_index'] = 0
        save_group_data(group_id)
    
    #更新出刀表
    if await safe_update_challenge_list(group_id) != 0:
        clanbattle_info[group_id]['failed_cnt'] += 1
        if clanbattle_info[group_id]['failed_cnt'] > 12: #连续炸一个小时就挂起
            halt_until_tomorrow(group_id)
            return 2
        else:
            return 1
    else:
        clanbattle_info[group_id]['failed_cnt'] = 0
    
    #检查现在是否在会战中
    if not get_daystr_from_daylist(group_id):
        group_config[group_id]['info'] = '公会战已结束' #能获取到日期列表但当天不在列表内 一定是公会战已结束 公会战开始前日期列表是空的
        halt_until_tomorrow(group_id)

    group_data[group_id]['battle_info'] = clanbattle_info[group_id]['battle_info']   #会战信息 用于判断新公会站开始
    save_group_data(group_id)
    return 0

        
#获取未推送的新出刀记录
def get_new_challenges(group_id: str) -> list:
    #上次同步位置
    if group_id not in group_data:
        return []
    index = group_data[group_id]['index']
    new_challenges = []
    #将index之后的新纪录加入新出刀记录表
    if len(all_challenge_list[group_id]) > index:
        for item in all_challenge_list[group_id][index:]:
            new_challenges.append(item)
    #处理完毕后更新指针 指向未来的第一条数据
    group_data[group_id]['index'] = len(all_challenge_list[group_id])
    save_group_data(group_id)
    return new_challenges

def check_reservation(group_id: str):
    rlist = []
    try:
        if group_id not in group_data:
            return rlist
        if 'name' not in clanbattle_info[group_id]['boss_info']:
            return rlist
        #boss状态 {name: "狂乱魔熊", total_life: 12000000, current_life: 2885013, lap_num: 1}
        clanbattle_info[group_id]['boss_info']
        #boss列表 [{id: "501", boss_name: "双足飞龙"}, {id: "502", boss_name: "野性狮鹫"}, {id: "503", boss_name: "雷电"},…]
        clanbattle_info[group_id]['boss_list'] 
        boss = -1
        for i in range(len(clanbattle_info[group_id]['boss_list'])):
            if clanbattle_info[group_id]['boss_list'][i]['boss_name'] == clanbattle_info[group_id]['boss_info']['name']:
                boss = i
                break
        if boss == -1:
            return rlist
        boss = str(boss)
        if len(group_data[group_id]['reservation'][boss]) == 0:
            return rlist
        rlist =  list(group_data[group_id]['reservation'][boss])
        group_data[group_id]['reservation'][boss] = []
        save_group_data(group_id)
        return rlist
    except:
        traceback.print_exc()
        return rlist

def add_reservation(group_id: str, boss: int, qqid: int):
    if group_id not in group_data:
        return '群组数据错误'
    if boss < 0 or boss > 4:
        return 'boss序号错误'
    boss = str(boss)
    rset = set(group_data[group_id]['reservation'][boss])
    rset.add(qqid)
    group_data[group_id]['reservation'][boss] = list(rset)
    save_group_data(group_id)
    return '预约成功'

def remove_reservation(group_id: str, boss: int, qqid: int):
    if group_id not in group_data:
        return '群组数据错误'
    if boss < 0 or boss > 4:
        return 'boss序号错误'
    boss = str(boss)
    rset = set(group_data[group_id]['reservation'][boss])
    rset.remove(qqid)
    group_data[group_id]['reservation'][boss] = list(rset)
    save_group_data(group_id)
    return '取消成功'


def remove_bind(group_id: str, name: str):
    if 'members' not in group_data[group_id]:   #游戏名-qq对应表
        return
    members = group_data[group_id]['members']
    for item in list(members):
        if item == name:
            group_data[group_id]['members'].pop(item)
    save_group_data(group_id)

#绑定成员
def add_bind(group_id: str, name: str, qq: int):
    if 'members' not in group_data[group_id]:   #游戏名-qq对应表
        group_data[group_id]['members'] = {}
    remove_bind(group_id, name)
    group_data[group_id]['members'][name] = qq
    group_data[group_id]['report_pause'] = False #解除暂停
    save_group_data(group_id)
    return 0
            
def get_bind_msg(group_id: str):
    msg = '绑定列表:\n'
    if 'members' not in group_data[group_id]:   #游戏名-qq对应表
        return msg
    for name in group_data[group_id]['members']:
        if name != magic_name:
            msg += f'[{name}]:{group_data[group_id]["members"][name]}\n'
    if magic_name in group_data[group_id]['members']:
        msg += f'其余未知成员:{group_data[group_id]["members"][magic_name]}\n'
    return msg

#计算指定时间到现在pcr时间有几天
def get_pcr_days_from(dt):
    pcr_today = datetime.datetime.now()
    #pcr_today = datetime.datetime(2020,8,25,20,0)
    if pcr_today.hour < 5:  #众所周知,兰德索尔的一天从凌晨5点开始
        pcr_today -= datetime.timedelta(days=1)
    pcr_today = pcr_today.replace(hour=5, minute=0, second=0, microsecond=0)
    return math.ceil((pcr_today - dt) / datetime.timedelta(days=1))

#从day_list获取会战第day天的日期字符串, day=0时取当天日期
def get_daystr_from_daylist(group_id: str, day: int = 0) -> str:
    day_list = []
    if day > 0:
        day = 0 - day #1 ~ 6 -> -1 ~ -6
        try:
            return clanbattle_info[group_id]['day_list'][day]
        except:
            pass
    elif day == 0:
        try:
            day_list = clanbattle_info[group_id]['day_list']
        except:
            return None
        for i in range(len(day_list)):
            day_str = day_list[i] #日期列表是降序的,第一位为最后一天
            dt = datetime.datetime(*map(int, day_str.split('-')))
            dt = dt.replace(hour=5, minute=30, second=0, microsecond=0)
            if get_pcr_days_from(dt) == 0:
                return day_str
    return None

def get_state_msg(group_id: str):
    msg = '当前状态:'
    if group_config[group_id]['state'] == 'run':
        msg += '运行中'
    elif group_config[group_id]['state'] == 'uninited':
        msg += '未初始化'
    elif group_config[group_id]['state'] == 'failed':
        msg += '异常'
    elif group_config[group_id]['state'] == 'halt':
        msg += '挂起'
    else:
        msg += '未知状态'
    
    if 'failed_cnt' in clanbattle_info[group_id] and clanbattle_info[group_id]['failed_cnt'] > 0:
        msg += f"\n异常计数:{clanbattle_info[group_id]['failed_cnt']}"
        msg += f"\n异常信息:{group_config[group_id]['info']}"
    elif group_config[group_id]['state'] != 'run':
        msg += f"\n异常信息:{group_config[group_id]['info']}"

    msg += '\n\n出刀记录推送:'
    if group_config[group_id]['push_challenge']:
        msg += '开启'
    else:
        msg += '关闭'
    msg += f'\n索引:{group_data[group_id]["index"]}'
    msg += '\n\n自动报刀:'
    if group_config[group_id]['report_mode'] == 'yobot_standalone':
        msg += 'yobot独立模式'
    elif group_config[group_id]['report_mode'] == 'yobot_embedded':
        msg += 'yobot嵌入模式'
    else:
        msg += '关闭'
    if group_config[group_id]['report_mode'] != 'disable':
        msg += f'\n索引:{group_data[group_id]["yobot_index"]}'
        msg += '\n状态:'
        if group_data[group_id]['report_pause']:
            msg += '暂停'
        else:
            msg += '运行中'
    return msg

async def check_update():
    global update_time
    data = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.github.com/repos/zyujs/clanbattle_info/commits') as resp:
                data = await resp.json(content_type='application/json')
    except:
        return False
    try:
        last_commit_time = data[0]['commit']['committer']['date']
        if update_time == '': #启动后第一次不报
            update_time = last_commit_time
        elif update_time != last_commit_time:
            update_time = last_commit_time
            return True
    except:
        return False
    return False

async def send_group_msg(bot, group_id: str, msg):
    try:
        await bot.send_group_msg(group_id=int(group_id), message = msg)
    except:
        traceback.print_exc()


def get_clanbattle_report_instance():
    plugins = nonebot.get_loaded_plugins()
    for plugin in plugins:
        m = str(plugin.module)
        m = m.replace('\\\\', '/')
        m = m.replace('\\', '/')
        if 'modules/clanbattle_report/report.py' in m:
            return plugin.module
    return None

def generate_data_for_clanbattle_report(group_id: str, nickname: str):
    result = {
        'code': 1,
        'msg': '无数据',
        'nickname': nickname,
        'clanname': '',
        'game_server': 'cn',
        'challenge_list': [],
        'background': 0,
    }
    try:
        result['clanname'] = clanbattle_info[group_id]['clan_info']['name']
    except:
        pass
    
    if group_id not in all_challenge_list:
        return

    for item in all_challenge_list[group_id]:
        if item['name'] == nickname:
            challenge = {
                'damage': item['damage'],
                'type': 0, #类型 0 普通 1 尾刀 2 补偿刀
                'boss': item['boss'],
                'cycle': item['lap_num'],
            }
            if item['kill'] != 0:
                challenge['type'] = 1
            elif item['reimburse'] != 0:
                challenge['type'] = 2
            result['challenge_list'].append(challenge)
    if len(result['challenge_list']) > 0:
        result['code'] = 0
    return result