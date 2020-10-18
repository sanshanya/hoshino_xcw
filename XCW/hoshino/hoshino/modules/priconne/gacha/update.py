# -*- coding: utf-8 -*-  #声明编码
import os, json, requests
from .. import _pcr_data
from nonebot import on_command
from hoshino import priv,Service
import hoshino,nonebot

sv_update = Service('gacha-update',visible=False,enable_on_default=True,manage_priv=priv.SUPERUSER)

NOTICE = 0  # 卡池更新完成时不需要提醒的, 可以把这里改成0

local_ver_path = './hoshino/modules/priconne/gacha/local_ver.json'
local_pool_path = './hoshino/modules/priconne/gacha/config.json'
local_pool_backup_path = './hoshino/modules/priconne/gacha/backup.json'

online_ver_url = 'https://api.redive.lolikon.icu/gacha/gacha_ver.json'
online_pool_url = 'https://api.redive.lolikon.icu/gacha/default_gacha.json'


def ids2names(ids:list):
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

def check_ver():
    '''
    检查版本, 返回版本号说明需要更新, 返回False不需要更新, 其他返回值则是HTTP状态码 \n
    并不会对本地文件做出任何修改
    '''

    # 获取本地版本号
    if os.path.exists(local_ver_path):
        with open(local_ver_path,'r') as lv:
            lvj = json.load(lv)
            local_ver = int(lvj["ver"])
    else:
        local_ver = 0
    hoshino.logger.info(f'检查卡池更新, 本地卡池版本{local_ver}')
    # 获取在线版本号
    try:
        ovj = requests.get(online_ver_url,timeout=10)
    except Exception as e:
        hoshino.logger.error(f'获取在线版本号时发生错误{type(e)}')
        return type(e)
        
    
    if ovj.status_code != 200:
        return ovj.status_code
    online_ver = int(ovj.json()["ver"])
    
    hoshino.logger.info(f'检查卡池更新, 在线卡池版本{online_ver}')
    if online_ver > local_ver:
        hoshino.logger.info(f'检测到新版本卡池, 正在更新')
        return online_ver
    else:
        hoshino.logger.info(f'未检测到新版本卡池,无需更新')
        return 0

def update_pool(online_ver):
    '''
    直接从API处获取在线卡池以及版本, 并覆盖到本地, 检测更新函数check_ver()中 
    传入参数是为了减少掉用次数
    当返回值为非0值时, 则返回的是HTTP状态码 
    '''

    # 获取在线卡池
    hoshino.logger.info(f'开始获取在线卡池')
    online_pool_f = requests.get(online_pool_url,timeout = 10)
    if online_pool_f.status_code != 200:
        hoshino.logger.error(f'获取在线卡池时发生错误{online_pool_f.status_code}')
        return online_pool_f.status_code
    online_pool = online_pool_f.json()

    # 读取本地默认卡池
    with open(local_pool_path,'r',encoding='utf-8') as lf:
        local_pool = json.load(lf)

    # 备份本地卡池
    hoshino.logger.info(f'开始备份本地卡池')
    with open(local_pool_backup_path,'w',encoding='utf-8') as backup:
        json.dump(local_pool,backup,indent=4,ensure_ascii=False)

    # 需要进行id转角色名的键
    ids_list = ['up','star3','star2','star1']
    # 服务器名称可能的键
    pool_name = {
        'BL':['BL','bl','Bl','bL','CN','cn'],
        'TW':['TW','tw','so-net','sonet'],
        'JP':['JP','jp'],
        'MIX':['MIX','mix','Mix','All','all','ALL']
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
    with open(local_pool_path,'w+',encoding='utf-8') as lf:
        json.dump(local_pool,lf,indent=4,ensure_ascii=False)

    # 更新本地版本号文件
    local_ver_json = {"ver":str(online_ver)}
    hoshino.logger.info(f'开始更新本地版本号文件')
    with open(local_ver_path,'w+',encoding='utf-8') as lvf:
        json.dump(local_ver_json,lvf,indent=4,ensure_ascii=False)

    return 0


@on_command('更新卡池',only_to_me=False)
async def demo_chat(session):
    '''
    强制更新卡池时试用此命令
    '''
    if not priv.check_priv(session.event,priv.SUPERUSER):
        return
    online_ver = check_ver()
    if type(online_ver) != int:
        await session.finish(f'检查版本发生错误{type(online_ver)}')
    if not online_ver:
        # 返回0则卡池最新
        await session.finish('当前卡池已为最新')
    if online_ver < 1000:
        # 版本号比这个大多了！
        await session.finish(f'检查版本发生错误{online_ver}')

    result = update_pool(online_ver)
    if result:
        await session.finish(f'更新过程中发生错误{result}')
    await session.finish(f'更新完成, 当前卡池版本号{online_ver}')
    
@sv_update.scheduled_job('cron',hour='16',minute='3')
async def update_gacha_sdj():
    bot = nonebot.get_bot()
    master_id = hoshino.config.SUPERUSERS[0]

    self_ids = bot._wsr_api_clients.keys()
    for id in self_ids:
        # 获取机器人自身ID
        sid = id

    online_ver = check_ver()
    if type(online_ver) != int and NOTICE:
        msg = f'检查版本发生错误{type(online_ver)}'
        await bot.send_private_msg(seld_id = sid,user_id=master_id, message=msg)
        return
    if not online_ver:
        # 返回0则卡池最新
        return

    if online_ver < 1000 and NOTICE:
        # 版本号比这个大多了！
        msg = f'检查版本发生错误{online_ver}'
        await bot.send_private_msg(seld_id = sid,user_id=master_id, message=msg)
        return

    result = update_pool(online_ver)
    if result and NOTICE:
        msg = f'更新过程中发生错误{result}'
        await bot.send_private_msg(seld_id = sid,user_id=master_id, message=msg)
        return

    
    if NOTICE: 
        msg = f'更新完成, 当前卡池版本号{online_ver}'      
        await bot.send_private_msg(seld_id = sid,user_id=master_id, message=msg)
