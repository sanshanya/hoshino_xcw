from .data_source import Record, get_user_quota, send_msg, show
from hoshino.service import Service
from hoshino.util4sh import Res as R
from aiocqhttp.event import Event
from hoshino.priv import get_user_priv
from hoshino.priv import *

RECORDS = Record().get_records()

sv = Service('我问你答')
@sv.on_rex(r'我问(.+?)你答.{0,1000}')
async def add_reply_for_self(bot, event: Event):
    uid = event['user_id']
    gid = event.get('group_id')
    user_priv = get_user_priv(event)
    user_quata = get_user_quota(user_priv)

    # mirai要下载图片
    await R.save_image(event)

    qu = event.raw_message.split('你答')[0].strip('我问').strip()
    ans = event.raw_message.split('你答')[1].strip()
    rec = Record(qu,ans,uid,gid,0)

    if rec.count_user_records(uid) >= user_quata:
        await bot.send(event, '您的额度不足,请删除记录后再来', at_sender=True)
        return

    if rec.insert_database():
        await bot.send(event,'问答添加成功',at_sender=True)    
        if rec.get_records:
            global RECORDS
            RECORDS = rec.get_records()
    else:
        await bot.send(event,'问答添加失败，问答不规范或者冲突',at_sender=True)

@sv.on_rex(r'有人问(.{1,1000})你答(.{0,1000})')
async def add_reply_for_group(bot, event):
    uid = event['user_id']
    gid = event.get('group_id')
    user_priv = get_user_priv(event)
    user_quata = get_user_quota(user_priv)

    await R.save_image(event)

    qu = event.raw_message.split('你答')[0].strip('有人问').strip()
    ans = event.raw_message.split('你答')[1].strip()
    rec = Record(qu, ans, uid, gid, 1)

    if rec.count_user_records(uid) >=user_quata:
        await bot.send(event,'您的额度不足,请删除记录后再来',at_sender=True)
        return

    if rec.insert_database():
        await bot.send(event,'问答添加成功',at_sender=True)
        if rec.get_records:
            global RECORDS
            RECORDS = rec.get_records()
    else:
        await bot.send(event,'问答添加失败，问答不规范或者冲突',at_sender=True)


#应该是不能正常删除图片触发，但是不想改了
@sv.on_prefix('删除问答')
async def delete_reply(bot, event: Event):
    global RECORDS
    gid = event.group_id
    uid = event.user_id
    qu = event.raw_message.strip('删除问答')
    rec = Record()

    if check_priv(event, SUPERUSER):
        if rec.delete_force(qu):
            RECORDS = rec.get_records()
            await bot.send(event,'问答删除成功')
        else:
            await bot.send(event, f'删除失败,可能该问答不存在')
        return

    if (qu,gid) not in RECORDS :
        await bot.send(event,'本群未找到该问答',at_sender=True)
        return

    if not check_priv(event, ADMIN) and uid != RECORDS[qu,gid]['rec_maker']:
        await bot.send(event,'只有管理员以上权限才能删除别人的问答',at_sender=True)
        return

    if rec.delete(qu,gid):
        RECORDS = rec.get_records()
        await bot.send(event,'问答删除成功')
    else:
        await bot.send(event,'神秘bug,删除失败',at_sender=True)
 
        
@sv.on_message()
async def send(bot,event: Event):
    qu = event.raw_message
    uid = event.user_id
    gid = event.group_id
    if (qu,gid) in RECORDS:
        rec = RECORDS[qu,gid]
        if rec['is_open'] == 0 and rec['rec_maker'] != uid:
            #人不对
            return
        reply = rec['answer']
        await send_msg(event,reply,at_sender=False)

@sv.on_prefix('查看问答')
async def show_group_reply(bot, event: Event):
    gid = event.get('group_id')
    try:
        page = int(event.raw_message.strip('查看问答'))
    except:
        page = 1
    records = {(m, n) : v for (m, n), v in RECORDS.items() if gid == n}
    reply, pages = show(records,page)
    await bot.send(event,reply.strip()+f'\n\n当前第{page}页，共{pages}页',at_sender=False)

@sv.on_prefix('查看所有问答')
async def show_all_reply(bot, event: Event):
    if not check_priv(event, SUPERUSER):
        await bot.send(event,'只有主人可以使用',at_sender=True)
        return 
    try:
        page = int(event.raw_message.strip('查看所有问答'))
    except:
        page = 1
    reply,pages = show(RECORDS,page)
    await bot.send(event,reply.strip()+f'\n\n当前第{page}页，共{pages}页',at_sender=False)

@sv.on_prefix('查看我问')
async def show_group_reply(bot, event: Event):
    gid = event.get('group_id')
    uid = event.user_id
    try:
        page = int(event.raw_message.strip('查看我问'))
    except:
        page = 1
    records = {(m, n) : v for (m, n), v in RECORDS.items() if gid == n and uid == RECORDS[(m, n)]['rec_maker']}
    reply, pages = show(records,page)
    await bot.send(event,reply.strip()+f'\n\n当前第{page}页，共{pages}页',at_sender=False)

            




