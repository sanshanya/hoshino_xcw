import os
import sqlite3
import math
from datetime import datetime,timedelta

from nonebot import get_bot 

import hoshino
from hoshino import R, Service, priv, util

sv_help = '''
- [挂树/取消挂树] 带计时的挂树功能,按55分钟算
- [合刀 A B C] 三个字母分别是刀1伤害/刀2伤害/剩余血量(国服)
'''.strip()

sv = Service(
    name = '合刀及挂树',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '会战', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助合刀及挂树"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

###挂树部分
@sv.on_command('挂树')
async def climb_tree(session):
    #获取上树成员以及其所在群信息
    ctx = session.ctx
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经上树，如果在挂树则提示，未挂树则上树
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree==1):
        msg = f'>>>挂树计时提醒[!]\n[CQ:at,qq={user_id}]已经挂树\n请勿重复上树'
    else:
        climb_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        climb_stime = datetime.now().strftime("%H:%M:%S")
        loss_time = (datetime.now()+timedelta(minutes=55)).strftime("%Y-%m-%d %H:%M:%S")
        loss_stime = (datetime.now()+timedelta(minutes=55)).strftime("%H:%M:%S")
        cur.execute(f"INSERT INTO tree VALUES(NULL,{user_id},{group_id},\"{loss_time}\")")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]开始挂树\n因上报时间与游戏时间存在误差\n挂树时长按照55分钟计算\n开始时间:{climb_stime}\n下树期限:{loss_stime}\n距离下树期限(约)10分钟时会连续提醒您三次\n如果没有人帮助请及时下树\n发送"取消挂树"可取消提醒'
    await session.send(msg)

@sv.on_command('取消挂树')
async def down_tree(session):
    #获取下树成员以及其所在群信息
    ctx = session.ctx
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    #连接挂树记录数据库
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    #查询当前状态是否已经下树，如果在挂树则删除记录，未挂树则提示错误
    query = cur.execute(f"SELECT COUNT(*) FROM tree WHERE qqid={user_id} AND gid={group_id}")
    for row in query:
        is_ontree = row[0]
    if(is_ontree==0):
        msg = f'>>>挂树计时提醒[!]\n[CQ:at,qq={user_id}]尚未挂树\n请勿申请下树'
    else:
        cur.execute(f"DELETE FROM tree WHERE qqid={user_id} AND gid={group_id}")
        con.commit()
        con.close()
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={user_id}]已经下树'
    await session.send(msg)

@sv.scheduled_job('interval', minutes=3)
async def ontree_scheduler():
    bot = get_bot()
    con = sqlite3.connect(os.getcwd()+"/hoshino/modules/ontree_scheduler/tree.db")
    cur = con.cursor()
    cur.execute("SELECT qqid,gid,loss_time FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime'))) BETWEEN 0 AND 600")
    query = cur.fetchall()
    for row in query:
        qq_id = row[0]
        group_id = row[1]
        loss_time = row[2][11:]
        if(".000" in loss_time):
            loss_time = loss_time[:-4]
        msg = f'>>>挂树计时提醒\n[CQ:at,qq={qq_id}]\n你的挂树剩余时间小于10分钟\n预计下树极限时间: {loss_time}\n请及时下树，防止掉刀\n发送"取消挂树"可取消提醒'
        await bot.send_group_msg(group_id=group_id, message=msg)
    cur.execute("DELETE FROM tree WHERE (strftime('%s',loss_time)-strftime('%s',datetime(strftime('%s','now'), 'unixepoch', 'localtime')))<0")
    con.commit()
    con.close()
    return
    
#####合刀部分    
@sv.on_prefix('合刀')
async def hedao(bot, event):
    shanghai = event.message.extract_plain_text().strip()
    shanghai = shanghai.split()
    if not shanghai:
        msg = '请输入：合刀 刀1伤害 刀2伤害 剩余血量\n如：合刀 50 60 70'
        await bot.finish(event, msg)
    if len(shanghai) != 3:
        return
    if is_number(shanghai[0]) is False:
        return
    if is_number(shanghai[1]) is False:
        return
    if is_number(shanghai[2]) is False:
        return
    dao_a = int(shanghai[0])
    dao_b = int(shanghai[1])
    current_hp = int(shanghai[2])
    if dao_a + dao_b < current_hp:
        await bot.finish(event, '当前合刀造成的伤害不能击杀boss')
    # a先出
    a_out = current_hp - dao_a
    a_per = a_out / dao_b
    a_t = (1 - a_per) * 90 + 10
    a_result = math.ceil(a_t)
    if a_result > 90:
        a_result = 90
    # b先出
    b_out = current_hp - dao_b
    b_per = b_out / dao_a
    b_t = (1 - b_per) * 90 + 10
    b_result = math.ceil(b_t)
    if b_result > 90:
        b_result = 90
    msg = f'{dao_a}先出，另一刀可获得{a_result}秒补偿刀\n{dao_b}先出，另一刀可获得{b_result}秒补偿刀'
    await bot.send(event, msg)


def is_number(s):
    '''判断是否是数字'''
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False