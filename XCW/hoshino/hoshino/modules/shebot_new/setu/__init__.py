import re
import os
import asyncio
from aiocqhttp.event import Event
import threading 

from os import path
from .api import get_final_setu_async
from .data_source import SetuWarehouse, save_config,load_config,send_setus
from .config import *
from hoshino.service import Service
from aiocqhttp.message import MessageSegment

g_config = load_config()
g_r18_groups = set(g_config.get('r18_groups',[]))
g_delete_groups = set(g_config.get('delete_groups',[]))

from hoshino.util4sh import Res as R
#初始化色图仓库
nr18_path = path.join(R.image_dir, 'nr18_setu') #存放非r18图片
r18_path = path.join(R.image_dir, 'r18_setu') #存放r18图片
search_path = path.join(R.image_dir, 'search_setu') #存放搜索图片
if not os.path.exists(search_path):
    os.mkdir(search_path)
wh = SetuWarehouse(nr18_path)
r18_wh = SetuWarehouse(r18_path,r18=1)

#启动一个线程一直补充色图
thd = threading.Thread(target=wh.keep_supply)
if ONLINE_MODE:
    print('线程启动')
    thd.start()

#启动一个线程一直补充r18色图
thd_r18 = threading.Thread(target=r18_wh.keep_supply)
if ONLINE_MODE:
    print('r18线程启动')
    thd_r18.start()

#设置limiter
from hoshino.util import DailyNumberLimiter, FreqLimiter
_num_limiter = DailyNumberLimiter(DAILY_MAX_NUM)
_freq_limiter = FreqLimiter(5)


from hoshino.priv import *
from hoshino.util4sh import download_async
sv = Service('涩图')
@sv.on_rex(r'^来?([1-5])?[份点张]?[涩色瑟]图(.{0,10})$')
async def send_common_setu(bot,event: Event):
    uid = event.user_id
    self_id = event.self_id
    gid = event.group_id
    user_priv = get_user_priv(event)
    is_to_delete = True if gid in g_delete_groups else False

    if not _num_limiter.check(uid):
        await bot.send(event, EXCEED_NOTICE)
        return

    if not _freq_limiter.check(uid):
        await bot.send(event, TOO_FREQUENT_NOTICE)
        return

    if not ONLINE_MODE:
        sv.logger.info('发送本地涩图')
        pic = R.get_random_image('nr18_setu')
        ret = await bot.send(event,  pic)
        msg_id = ret['message_id']
        if is_to_delete:
            #30秒后删除
            await asyncio.sleep(30)
            await bot.delete_msg(self_id=self_id, message_id=msg_id)
        return

    robj = event['match']
    try:
        num = int(robj.group(1))
    except:
        num = 1

    #按照数量设置limiter
    _num_limiter.increase(uid,num)
    _freq_limiter.start_cd(uid,num*5)

    keyword = robj.group(2).strip()
    if keyword:
        await bot.send(event, '正在搜索，请稍等~')
        sv.logger.info(f'含有关键字{keyword}，尝试搜索')
        if user_priv < SUPERUSER:
            setus = await get_final_setu_async(search_path,keyword=keyword,r18=0)
        else:
            setus = await get_final_setu_async(search_path,keyword=keyword,r18=2) 
        if not setus:
            await bot.send(event, f'没有找到关键字{keyword}的涩图，您将被禁用涩图服务60s')
            _freq_limiter.start_cd(uid, 60)
            sv.logger.info(f'{uid} searched keyword {keyword} and returned no result')
            return
        setu = setus[0]
        pic_path = await download_async(setu.url, search_path, setu.pid)
        pic = MessageSegment.image(pic_path)
        reply = f'{setu.title}\n画师：{setu.author}\npid:{setu.pid}{pic}'
        try:
            await bot.send(event,reply,at_sender=False)
            _num_limiter.increase(uid)
            _freq_limiter.start_cd(uid, 30)
        except Exception as ex:
            await bot.send(event, f'搜索关键字{keyword}发生异常')
            sv.logger.error(f'搜索涩图时发生异常 {ex}')
    else:
        setus = wh.fetch(num)
        if not setus:#send_setus为空
            await bot.send(event,'色图库正在补充，下次再来吧',at_sender=False)
            return
        else:
            await send_setus(bot,event,'nr18_setu', setus, WITH_URL, is_to_delete)            

@sv.on_fullmatch('就这不够色')
async def send_r18_setu(bot, event):
    uid = event['user_id']
    gid = event.get('group_id',0)
    is_to_delete = True if gid in g_delete_groups else False
    self_id = event['self_id']

    if gid not in g_r18_groups and gid!= 0:
        await bot.send(event,'本群未开启r18色图，请私聊机器人,但注意不要过分请求，否则拉黑')
        return

    if not _num_limiter.check(uid):
        await bot.send(event, EXCEED_NOTICE)
        return

    if not _freq_limiter.check(uid):
        await bot.send(event, TOO_FREQUENT_NOTICE)
        return

    if not ONLINE_MODE:
        sv.logger.info('发送本地r18涩图')
        pic = R.get_random_image('r18_path')
        ret = await bot.send(event,pic)

        msg_id = ret['message_id']
        if is_to_delete:
            await asyncio.sleep(30)
            await bot.delete_msg(self_id=self_id, message_id=msg_id)
        return   

    _num_limiter.increase(uid)
    _freq_limiter.start_cd(uid)

    setus = r18_wh.fetch(1)
    sv.logger.info('发送r18图片')
    await send_setus(bot, event, 'r18_setu', setus, WITH_URL, is_to_delete)

@sv.on_message()
async def switch(bot, event):
    global g_is_online
    global g_delete_groups
    global g_config
    global g_r18_groups
    msg = event['raw_message']
    gid = event.get('group_id')
    if get_user_priv(event) < SUPERUSER:
        return

    elif msg == '本群涩图撤回':
        g_delete_groups.add(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(event,'本群涩图撤回',at_sender=True)

    elif msg == '本群涩图不撤回':
        g_delete_groups.discard(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(event,'本群涩图不撤回',at_sender=True)

    elif re.match(r'群(\d{5,12})?涩图撤回',msg):
        gid = int(re.match(r'群(\d{5,12})?涩图撤回',msg).group(1))
        g_delete_groups.add(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(event,f'群{gid}涩图撤回')

    elif re.match(r'群(\d{5,12})?涩图不撤回',msg):
        gid = int(re.match(r'群(\d{5,12})?涩图不撤回',msg).group(1))
        g_delete_groups.discard(gid)
        g_config['delete_groups'] = list(g_delete_groups)
        save_config(g_config)
        await bot.send(event,f'群{gid}涩图不撤回')

    elif msg == '本群r18开启':
        g_r18_groups.add(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(event,'本群r18开启',at_sender=True)

    elif msg == '本群r18关闭':
        g_r18_groups.discard(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(event,'本群r18关闭',at_sender=True)

    elif re.match(r'群(\d{5,12})r18开启',msg):
        gid = int(re.match(r'群(\d{5,12})r18开启',msg).group(1))
        g_r18_groups.add(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(event,f'群{gid}r18开启')

    elif re.match(r'群(\d{5,12})r18关闭',msg):
        gid = int(re.match(r'群(\d{5,12})r18关闭',msg).group(1))
        g_r18_groups.discard(gid)
        g_config['r18_groups'] = list(g_r18_groups)
        save_config(g_config)
        await bot.send(event,f'群{gid}r18关闭')

    else:
        pass




            
        

            
