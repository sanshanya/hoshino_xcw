# -*- coding: utf-8 -*-
from os import stat
from nonebot import on_command, get_bot, scheduler
from requests.sessions import session
from hoshino import aiorequests, priv
from ast import literal_eval
import hoshino
import os, json
from .. import _pcr_data
from ..chara import download_chara_icon, roster

# 卡池更新是否通知管理员
NOTICE = False  


# 是否自动更新缺失的角色数据并下载图标, 是否重载花名册
# 此选项会使您的仓库存在未提交的修改, 如果有影响请注意处理
PCRDATA_UPDATA = True

local_ver_path = os.path.join(os.path.dirname(__file__), 'local_ver.json')
local_pool_path = os.path.join(os.path.dirname(__file__), 'config.json')
local_pool_backup_path = os.path.join(os.path.dirname(__file__), 'backup.json')


online_ver_url = 'https://api.redive.lolikon.icu/gacha/gacha_ver.json'
online_pool_url = 'https://api.redive.lolikon.icu/gacha/default_gacha.json'
online_pcr_data_url = 'https://api.redive.lolikon.icu/gacha/unitdata.py'


async def get_online_pcrdata():
    '''
    获取在线的角色数据信息, 并处理为json格式
    '''
    online_pcrdata = await aiorequests.get(url=online_pcr_data_url, timeout=10, verify=False)
    if online_pcrdata.status_code != 200:
        hoshino.logger.error(f'获取在线角色数据时发生错误{online_pcrdata.status_code}')
        return {}

    # 移除开头的'CHARA_NAME = ', 格式化为json便于处理
    online_pcrdata_text = await online_pcrdata.text
    online_pcrdata_text = online_pcrdata_text.replace('CHARA_NAME = ', '')
    online_pcrdata_json = literal_eval(online_pcrdata_text)
    return online_pcrdata_json


async def update_pcrdata():
    '''
    对比本地和远程的_pcr_data.py, 自动补充本地没有的角色信息, 已有角色信息不受影响
    '''
    online_pcrdata = await get_online_pcrdata()
    
    hoshino.logger.info('开始对比角色数据')
    if online_pcrdata == {}:
        return -1
    for id in online_pcrdata:
        if id not in _pcr_data.CHARA_NAME and id != 9401:
            hoshino.logger.info(f'已开始更新角色{id}的数据和图标')
            # 由于返回数据可能出现全半角重复, 做一定程度的兼容性处理, 会将所有全角替换为半角, 并移除重复别称
            for i, name in enumerate(online_pcrdata[id]):
                name_format = name.replace('（', '(')
                name_format = name_format.replace('）', ')')
                online_pcrdata[id][i] = name_format

            # 转集合再转列表, 移除重复元素
            online_pcrdata[id] = list(set(online_pcrdata[id]))
            _pcr_data.chara_master.add_chara(id, online_pcrdata[id])
            download_chara_icon(id, 6)
            download_chara_icon(id, 3)
            download_chara_icon(id, 1)
    # 重载花名册(不会引起全局reload)
    roster.update()


def ids2names(ids: list) -> list:
    '''
    根据ID转换为官方译名,为了与现行卡池兼容
    '''
    res = []
    for id in ids:
        if id in _pcr_data.CHARA_NAME:
            res.append(_pcr_data.CHARA_NAME[id][0])
        else:
            hoshino.logger.warning(f'缺少角色{id}的信息, 请注意更新静态资源')
    return res


def get_local_ver() -> int:
    '''
    获取本地版本号
    '''
    if os.path.exists(local_ver_path):
        with open(local_ver_path, 'r') as lv:
            lvj = json.load(lv)
            local_ver = int(lvj["ver"])
    else:
        local_ver = 0
    hoshino.logger.info(f'检查卡池更新, 本地卡池版本{local_ver}')
    return local_ver


async def get_online_ver() -> int:
    '''
    获取在线版本号
    '''
    online_pool_ver = await aiorequests.get(url=online_ver_url, timeout=10, verify=False)

    if online_pool_ver.status_code != 200:
        hoshino.logger.error(f'获取在线卡池版本时发生错误{online_pool_ver.status_code}')
        return online_pool_ver.status_code
    online_pool_ver_json = await online_pool_ver.json()
    online_ver = int(online_pool_ver_json["ver"])

    hoshino.logger.info(f'检查卡池更新, 在线卡池版本{online_ver}')
    return online_ver


def update_local_ver(ver: int) -> None:
    '''
    修改本地版本号
    '''
    local_ver_json = {"ver": str(ver)}
    hoshino.logger.info(f'写入本地版本号文件')
    with open(local_ver_path, 'w+', encoding='utf-8') as lvf:
        json.dump(local_ver_json, lvf, indent=4, ensure_ascii=False)


async def get_online_pool():
    '''
    获取在线卡池, 返回json格式
    '''
    hoshino.logger.info(f'开始获取在线卡池')
    online_pool_f = await aiorequests.get(online_pool_url, timeout=10, verify=False)
    if online_pool_f.status_code != 200:
        hoshino.logger.error(f'获取在线卡池时发生错误{online_pool_f.status_code}')
        return online_pool_f.status_code
    online_pool = await online_pool_f.json()
    return online_pool


def update_local_pool(online_pool) -> None:
    '''
    更新本地卡池文件, 并备份原卡池
    '''
    # 读取本地卡池
    with open(local_pool_path, 'r', encoding='utf-8') as lf:
        local_pool = json.load(lf)

    # 备份本地卡池
    hoshino.logger.info(f'开始备份本地卡池')
    with open(local_pool_backup_path, 'w', encoding='utf-8') as backup:
        json.dump(local_pool, backup, indent=4, ensure_ascii=False)

    # 需要进行id转角色名的键
    ids_list = ['up', 'star3', 'star2', 'star1']
    # 服务器名称可能的键
    pool_name = {
        'BL': ['BL', 'bl', 'Bl', 'bL', 'CN', 'cn'],
        'TW': ['TW', 'tw', 'so-net', 'sonet'],
        'JP': ['JP', 'jp'],
        'MIX': ['MIX', 'mix', 'Mix', 'All', 'all', 'ALL']
    }

    for server in pool_name:
        for online_pool_name in online_pool:
            if online_pool_name in pool_name[server]:
                # 仅当命中时才更新卡池, 如果网站删除一个卡池, 更新后不会影响本地卡池
                local_pool[server] = online_pool[online_pool_name]
                # 检查UP角色是重复在star3中出现
                if local_pool[server]['up'] != []:
                    up_chara_id = local_pool[server]['up'][0]
                    if up_chara_id in local_pool[server]['star3']:
                        local_pool[server]['star3'].remove(up_chara_id)
                # 角色名转id
                for star in ids_list:
                    local_pool[server][star] = ids2names(local_pool[server][star])
                    if local_pool[server][star] == []:
                        # MIX池会出现无UP角色的空列表, 然后偷偷换成我老婆
                        local_pool[server][star] = ['镜华(万圣节)']
                        hoshino.logger.info(f'{server}卡池{star}列表为空, 已替换为镜华(万圣节)')

    # 将新卡池写入文件
    hoshino.logger.info(f'开始写入本地卡池文件')
    with open(local_pool_path, 'w+', encoding='utf-8') as lf:
        json.dump(local_pool, lf, indent=4, ensure_ascii=False)


async def update_pool(force=False) -> int:
    '''
    从远程拉取卡池覆盖本地的卡池
    1, 备份原卡池到backup.json
    2, 从远程卡池获取数据, 修改本地卡池数据
    3, 从远程卡池获取版本号, 覆盖到本地
    指定force为true, 则不会比较本地版本号是否最新
    '''
    if PCRDATA_UPDATA:
        await update_pcrdata()
    # 获取远程卡池
    online_pool = await get_online_pool()
    if type(online_pool) == int:
        hoshino.error(f'获取在线卡池时发生错误{online_pool}')
        return online_pool

    # 获取远程版本号
    online_ver = await get_online_ver()
    if online_ver < 1000:
        hoshino.error(f'获取在线卡池版本时发生错误{online_ver}')
        return online_ver

    # 比较本地版本号
    local_ver = get_local_ver()
    if force:
        # 指定强制更新
        local_ver = 0
    if online_ver <= local_ver:
        return 0
    # 修改本地卡池
    update_local_pool(online_pool)
    # 覆盖本地版本号
    update_local_ver(online_ver)
    return online_ver


@on_command('更新卡池', only_to_me=False)
async def update_pool_chat(session):
    '''
    手动更新卡池时试用此命令
    '''
    if not priv.check_priv(session.event, priv.ADMIN):
        return
    status = await update_pool()
    if status == 0:
        await session.finish('已是最新版本, 仍要更新卡池请使用【强制更新卡池】命令')
    elif status < 1000:
        await session.finish(f'发生错误{status}')
    else:
        await session.finish(f'更新完成, 当前卡池版本{status}')


@on_command('强制更新卡池', only_to_me=False)
async def update_pool_force_chat(session):
    '''
    强制更新卡池
    '''
    if not priv.check_priv(session.event, priv.SUPERUSER):
        return
    status = await update_pool(force=True)
    if status == 0:
        await session.finish(f'状态{status}')
    elif status < 1000:
        await session.finish(f'发生错误{status}')
    else:
        await session.finish(f'更新完成, 当前卡池版本{status}')


@scheduler.scheduled_job('cron', hour='17', minute='05')
async def update_pool_sdj():
    bot = get_bot()
    master_id = hoshino.config.SUPERUSERS[0]

    self_ids = list(bot._wsr_api_clients)
    sid = self_ids[0]

    status = await update_pool()
    if status == 0:
        return 
    elif status < 1000 and NOTICE:
        msg = f'自动更新卡池时发生错误{status}'
        await bot.send_private_msg(seld_id=sid, user_id=master_id, message=msg)
    elif NOTICE:
        msg = f'已自动更新卡池，当前版本{status}'
        await bot.send_private_msg(seld_id=sid, user_id=master_id, message=msg)