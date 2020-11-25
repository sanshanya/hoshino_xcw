
from hoshino.config.__bot__ import SUPERUSERS
from datetime import timedelta, datetime
from math import ceil

import random, string
import os
import time, json
import asyncio
import nonebot, hoshino

from .constant import key_dict, group_dict, trial_list, config



def generate_key():
    '''
    生成16位卡密
    '''
    begin=config.BEGIN
    new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16-len(begin)))
    while new_key in key_dict:  # 防止生成重复的卡密, 不过概率太低了。。。
        new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16-len(begin)))
    new_key = begin + new_key
    return new_key


def add_key(duration):
    '''
    卡密添加到数据库中
    '''
    new_key = generate_key()
    key_dict[new_key] = duration
    return new_key


def get_key_list():
    '''
    获取全部的卡密列表
    '''
    key_list = []
    for key, value in key_dict.iteritems():
        key_list.append({'key': key, 'duration': value})
    return key_list


def del_key(key):
    '''
    删除一张卡密, 成功返回True
    '''
    if key in key_dict:
        key_dict.pop(key)
        return True
    return False


def update_key(key, duration):
    '''
    更新一张卡密,成功返回True
    '''
    if duration <= 0:
        # 禁止将有效期更新为0, 因为检验卡密时以0为无效标志
        return False
    if key in key_dict:
        key_dict[key] = duration
        return True
    return False


def query_key(key):
    '''
    检查一张卡密, 有效则返回可以增加的授权时间, 无效则返回0
    '''
    if key in key_dict:
        return key_dict[key]
    else:
        return 0


def check_group(gid):
    '''
    检查一个群是否有授权, 如果有返回过期时间（datetime格式）, 否则返回False. 
    注意无论Bot是否加入此群都会返回
    '''
    if gid in group_dict:
        return group_dict[gid]
    else:
        return 0


async def reg_group(gid, key):
    '''
    为一个群充值, 卡密无效则返回False, 否则返回剩余有效期（datatime格式）
    '''
    days = query_key(key)
    if days == 0:
        return False
    past_time = await change_authed_time(gid, days)
    del_key(key)
    return past_time


async def change_authed_time(gid, time_change=0, operate=''):
    '''
    不使用卡密, 而直接对一个群的授权时间进行操作
    '''
    if operate == 'clear':
        try:
            # 用try是因为可能会尝试给本来就无授权的群清空授权, 此种情况并不需要另外通知, 因为最终目的一致
            group_dict.pop(gid)
        except:
            pass
        await flush_group()
        return 0

    if gid in group_dict:
        group_dict[gid] = group_dict[gid] + timedelta(days=time_change)
    else:
        today = datetime.now()
        group_dict[gid] = today + timedelta(days=time_change)
        await flush_group()
    return group_dict[gid]

async def get_nickname(user_id):
    '''
    获取用户昵称
    '''
    uid = user_id
    user_info = await nonebot.get_bot().get_stranger_info(user_id=uid)
    return user_info['nickname']


async def get_group_info(group_ids=0, info_type='group_name'):
    '''
    1. 传入一个整型数字, 返回单个群指定信息, 格式为字典
    2. 传入一个list, 内含多个群号(int), 返回一个字典, 键为群号, 值为指定信息
    3. 不填入参数, 返回一个包含所有群号与指定信息的字典
    无论获取多少群信息, 均只有一次API的开销, 传入未加入的群时, 将自动忽略
    info_type支持group_id, group_name, max_member_count, member_count
    '''
    group_info_all = await get_group_list_all()
    _gids = []
    _gnames = []
    # 获得的已加入群为列表形式, 处理为需要的字典形式
    for it in group_info_all:
        _gids.append(it['group_id'])
        _gnames.append(it[info_type])
    group_info_dir = dict(zip(_gids, _gnames))

    if group_ids == 0:
        return group_info_dir
    if type(group_ids) == int:
        # 转为列表
        group_ids = [group_ids]
        print(group_ids)

    for key in list(group_info_dir.keys()):
        if key not in group_ids:
            del group_info_dir[key]
        else:
            # TODO: group not joined
            pass
    return group_info_dir


async def get_authed_group_list():
    '''
    获取已授权的群
    '''
    authed_group_list = []
    group_name_dir = await get_group_info()

    for key, value in group_dict.iteritems():
        deadline = f'{value.year}年{value.month}月{value.day}日 {value.hour}时{value.minute}分'
        group_name = group_name_dir.get(int(key), '未知')
        authed_group_list.append({'gid': key, 'deadline': deadline, 'groupName': group_name})
    return authed_group_list


async def get_group_list_all():
    '''
    获取所有群, 无论授权与否, 返回为原始类型(列表)
    '''
    bot = nonebot.get_bot()
    self_ids = bot._wsr_api_clients.keys()
    for sid in self_ids:
        group_list = await bot.get_group_list(self_id=sid)
    return group_list


async def process_group_msg(gid, expiration, title: str = '', end='', group_name_sp=''):
    '''
    把查询消息处理为固定的格式 \n
    第一行为额外提醒信息（例如充值成功）\n
    群号：<群号> \n
    群名：<群名> \n
    授权到期：<到期时间> \n
    部分情况下, 可以通过指定群组名的方式来减少对API的调用次数（我并不知道这个对性能是否有大影响）
    '''
    if group_name_sp == '':
        bot = nonebot.get_bot()
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            try:
                group_info = await bot.get_group_info(self_id=sid, group_id=gid)
                group_name = group_info['group_name']
            except:
                group_name = '未知(Bot未加入此群)'
    else:
        group_name = group_name_sp
    time_format = expiration.strftime("%Y-%m-%d %H:%S:%M")
    msg = title
    msg += f'群号：{gid}\n群名：{group_name}\n到期时间：{time_format}'
    msg += end
    return msg


async def new_group_check(gid):
    '''
    加入新群时检查此群是否符合条件,如果有试用期则会自动添加试用期授权时间, 同时添加试用标志
    '''
    if gid in group_dict:
        time_left = group_dict[gid] - datetime.now()

        if time_left.total_seconds() <= 0:
            # 群在列表但是授权过期, 从授权列表移除此群
            group_dict.pop(gid)
            await flush_group()
            return 'expired'
        await flush_group()
        return 'authed'

    if config.NEW_GROUP_DAYS <= 0 or gid in trial_list:
        return 'no trial'
    # 添加试用标记
    trial_list[gid] = 1
    # 添加试用天数
    await change_authed_time(gid=gid, time_change=config.NEW_GROUP_DAYS)
    return 'trial'


async def transfer_group(old_gid, new_gid):
    '''
    转移授权,新群如果已经有时长了则在现有时长上增加
    '''
    today = datetime.now()
    left_time = group_dict[old_gid] - today if old_gid in group_dict else timedelta(days=0)
    group_dict[new_gid] = left_time + (group_dict[new_gid] if new_gid in group_dict else today)
    group_dict.pop(old_gid)
    await flush_group()

async def gun_group(group_id, reason='管理员操作'):
    '''
    退出群聊, 同时会发送消息, 说明退群原因
    '''
    gid = group_id
    msg = config.GROUP_LEAVE_MSG
    msg += reason
    try:
        await nonebot.get_bot().send_group_msg(group_id=gid, message=msg)
    except Exception as e:
        hoshino.logger.error(f'向群{group_id}发送退群消息时发生错误{e}')
    await asyncio.sleep(2)
    try:
        await nonebot.get_bot().set_group_leave(group_id=gid)
    except nonebot.CQHttpError:
        return False
    return True


async def notify_group(group_id, txt):
    '''
    发送自定义提醒广播,顺带解决了HoshinoBot和Yobot的广播短板
    '''
    gid = group_id
    try:
        await nonebot.get_bot().send_group_msg(group_id=gid, message=txt)
    except nonebot.CQHttpError:
        return False
    return True

async def notify_master(txt):
    '''
    通知主人
    '''
    try:
        await nonebot.get_bot().send_private_msg(user_id=SUPERUSERS[0], message=txt)
    except nonebot.CQHttpError:
        return False
    return True
    

def time_now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


LOG_LIST = [
    'card_use',
    'group_add',
    'group_kick',
    'group_leave',
    'friend_add',
    'number_check'
]


def log(info, log_type='debug'):
    '''
    记录日志, 保存位置为HoshinoBot/logs/authMS.log
    '''
    if not config.LOG:
        return
    if not config.DEBUG and log_type not in LOG_LIST:
        # 非DEBUG模式, 非需要记录的信息
        return

    file_name = 'log/authMS.log'
    with open(file_name, 'a', encoding='utf-8') as l:
        l.writelines(f"[{time_now()}]")
        l.writelines(info)
        l.writelines('\n')


def allowlist(group_id, operator='none', nocheck='no_number_check'):
    '''
    operator------
        none: 检查一个群或人是否在白名单中, 不在时返回值为not in
        add: 增加白名单
        del: 移除白名单
        clear: 清除所有白名单
    nocheck------
        no_number_check: 不检查人数
        no_auth_check: 不检查授权(永久有效)
        no_check: 全部不检查
    '''

    ALLOWLIST_PATH = os.path.expanduser('~/.hoshino/authMS/allowlist.json')
    if os.path.exists(ALLOWLIST_PATH):
        with open(ALLOWLIST_PATH, 'r', encoding='utf-8') as rf:
            try:
                allowlist = json.load(rf)
            except Exception as e:
                # 您写的json格式有错误？扬了就好了
                hoshino.logger.error(f'读取白名单列表时发生错误{type(e)}')
                allowlist = {}
    else:
        os.makedirs(os.path.expanduser('~/.hoshino/authMS'), exist_ok=True)
        allowlist = {}

    if operator == 'none':
        return allowlist.get(str(group_id), 'not in')
    elif operator == 'add':
        allowlist[str(group_id)] = nocheck
        hoshino.logger.error(f'已将群{group_id}添加到白名单，类型为{nocheck}')
        rt = 'ok'
    elif operator == 'remove':
        rt = allowlist.pop(str(group_id), 'not in')
        if rt != 'not in':
            hoshino.logger.error(f'已将群{group_id}移除白名单')
            rt = 'ok'
        else:
            hoshino.logger.error(f'群{group_id}移除不在白名单，移除失败')
    elif operator == 'clear':
        allowlist.clear()
        hoshino.logger.error(f'已清空所有白名单')
        rt = 'ok'
    else:
        return 'nothing to do'

    with open(ALLOWLIST_PATH, "w", encoding='utf-8') as sf:
        json.dump(allowlist, sf, indent=4, ensure_ascii=False)

    return rt


# 这个没写完别看了-------------------------------------------
async def set_block_list(group_id, operator_id, reason='no reason'):
    '''
    将一个群添加到黑名单, 目前仅本地拉黑, 未来可能支持......算了不画饼了
    可以重复拉黑, 以更新reason

    group_id: 要拉黑的群号
    operator_id: 操作人
    reason: 拉黑原因

    以下信息将由api自动获取:
    group_info: 直接传入bot.get_group_info()返回的原始信息
    group_member_list: 直接传入bot.get_group_member_list()返回的群所有成员信息
    operator_name: 操作者昵称
    '''

    BLOCKLIST_PATH = os.path.expanduser('~/.hoshino/authMS/blocklist.json')

    # 读名单
    if os.path.exists(BLOCKLIST_PATH):
        with open(BLOCKLIST_PATH, 'r+', encoding='utf-8') as f:
            blocklist = json.load(f)
    else:
        os.makedirs(os.path.expanduser('~/.hoshino/authMS'), exist_ok=True)
        blocklist = {}

    bot = nonebot.get_bot

    # 在对应黑白名单中加入该群, 键值为群号
    temp_dir = {
        "time": int(time.time()),  # 记录为时间戳形式, 便于处理    
        "operator_id": int(operator_id),
        "operator_name": 'name'
    }
    pass


def get_list(list_type='allowlist'):
    '''
    list_type可选blocklist和allowlist
    保存位置: ~./.hoshino/authMS/blocklist.json和allowlist.json
    为保持兼容性, 会将所有键值转化为int
    '''
    LIST_PATH = os.path.expanduser(f'~/.hoshino/authMS/{list_type}.json')
    if os.path.exists(LIST_PATH):
        with open(LIST_PATH, 'r', encoding='utf-8') as rf:
            try:
                ba_list = json.load(rf)
            except Exception as e:
                print(e)
                ba_list = {}
    else:
        ba_list = {}

    # 将键的str格式转换为int格式, 保持其他函数传参时的兼容性
    ba_new = {}
    for key in ba_list:
        ba_new[int(key)] = ba_list[key]
    return ba_new


async def flush_group():
    with open(config.EVENT_FILTER, mode="r", encoding='utf-8') as f:
        fil = json.load(f)
    fil[".or"][0]["group_id"][".in"] = []
    group_list = []
    for key, val in group_dict.iteritems():
        group_list.append(key)
    fil[".or"][0]["group_id"][".in"] = group_list
    with open(config.EVENT_FILTER, mode="w", encoding='utf-8') as f:
        json.dump(fil, f, indent=4, ensure_ascii=False)
    await nonebot.get_bot().call_action("reload_event_filter")
