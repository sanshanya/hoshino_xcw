from io import BytesIO
import os
import requests
import aiohttp
import hoshino
from PIL import Image
from datetime import datetime
from hoshino import Service
from hoshino import Service, priv as Priv
from hoshino.util import FreqLimiter
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from .data_source import add_text,get_apikey,add_text1,get_GmServer
import base64
background1 = '离职报告模板.jpg'
background2 = '公会报告模板.jpg'
_time_limit = 30#频率限制
_lmt = FreqLimiter(_time_limit)
yobot_url = hoshino.config.public_address#改成你的yobot网址
year = datetime.now().strftime('%Y')#年
month = str(int(datetime.now().strftime('%m')))#去0的月
sv = Service('公会战报告书')
def pcr_constellations(month):
    constellations = ["处女", "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼", "白羊", "金牛", "双子", "巨蟹", "狮子"]#台服的会战顺序(按月)
    b_constellations = ["摩羯","水瓶","双鱼","白羊","金牛","双子","巨蟹","狮子","处女","天秤","天蝎","射手"]#国服的（预测） 
    if game_server =="cn":
        for x in range(1,13):
            if x == int(month)-1:
                li = b_constellations[x-1]
                return li
                break
            else:
                continue
    elif game_server == "tw":
        for x in range(1,13):
            if x == int(month)-1:
                li = constellations[x-1]
                return li
                break
            else:
                continue
    else:
        return

    '''
    for x in range(1,13):
        if x == int(month)-1:
            li = constellations[x-1]
            return li
            break
        else:
            continue
    '''
@sv.on_keyword(keywords='生成离职报告')
async def create_resignation_report(bot, event):
    uid = event['user_id']
    #nickname = event['sender']['nickname']
    gid = event['group_id']
    apikey = get_apikey(gid)
    global game_server
    game_server = get_GmServer(gid)
    url = f'{yobot_url}/yobot/clan/{gid}/statistics/api/?apikey={apikey}'
    if not _lmt.check(uid):
        await bot.send(event, f'{_time_limit}秒仅能生成一次报告', at_sender=True)
        return
    
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    if clanname == 0:
        await bot.send(event, f'！当前没有创建公会，无法使用')
        return
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
            if nickname == 0:
                await bot.send(event, f'未加入公会或已从公会离职，无法生成报告')
                return
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    if total_chl == 0:
        await bot.send(event, f'没有查询到出刀数据，请出刀后再试')
        return
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['health_ramain'] != 0 and chl['is_continue'] == 0:
            damage_to_boss[chl['boss_num']-1] += chl['damage']
            truetimes_to_boss[chl['boss_num']-1] += 1
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    for chl in challenges[::-1]:
        if chl['damage'] != 0 or chl['is_continue']:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x()+0.1, h, f'{int(times_to_boss[i])}刀',fontdict={"size":12})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background1))
    img.paste(bar_img1, (580,950), mask=bar_img1.split()[3])
    img.paste(bar_img2, (130,950), mask=bar_img2.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    #year = '2020'
    #month = '7'
    #constellation = '双子'
    
    add_text(img, row1, position=(380,630), textsize=35)
    add_text(img, row2, position=(833,630), textsize=35)
    add_text(img, year, position=(355,438), textsize=40)
    add_text(img, month, position=(565,438), textsize=40)
    add_text(img, pcr_constellations(month), position=(710,438), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 520), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(280,365), textsize=35)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')
    _lmt.start_cd(uid)

@sv.on_keyword(keywords='生成会战报告')
async def create_resignation_report(bot, event):
    uid = event['user_id']
    #nickname = event['sender']['nickname']
    gid = event['group_id']
    apikey = get_apikey(gid)
    global game_server
    game_server = get_GmServer(gid)
    url = f'{yobot_url}/yobot/clan/{gid}/statistics/api/?apikey={apikey}'
    if not _lmt.check(uid):
        await bot.send(event, f'{_time_limit}小时仅能生成一次报告', at_sender=True)
        return
    
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    if clanname == 0:
        await bot.send(event, f'！当前没有创建公会，无法使用')
        return
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
            if nickname == 0:
                await bot.send(event, f'未加入公会或已从公会离职，无法生成报告')
                return
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    if total_chl == 0:
        await bot.send(event, f'没有查询到出刀数据，请出刀后再试')
        return
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['health_ramain'] != 0 and chl['is_continue'] == 0:
            damage_to_boss[chl['boss_num']-1] += chl['damage']
            truetimes_to_boss[chl['boss_num']-1] += 1
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    for chl in challenges[::-1]:
        if chl['damage'] != 0 or chl['is_continue']:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x()+0.1, h, f'{int(times_to_boss[i])}刀',fontdict={"size":12})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background2))
    img.paste(bar_img1, (580,950), mask=bar_img1.split()[3])
    img.paste(bar_img2, (130,950), mask=bar_img2.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    #year = '2020'
    #month = '7'
    #constellation = '双子'
    
    add_text(img, row1, position=(380,630), textsize=35)
    add_text(img, row2, position=(833,630), textsize=35)
    add_text(img, year, position=(355,438), textsize=40)
    add_text(img, month, position=(565,438), textsize=40)
    add_text(img, pcr_constellations(month), position=(710,438), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 520), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(280,365), textsize=35)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')
    _lmt.start_cd(uid)


@sv.on_rex(r'^看看报告$')#, normalize=False)
async def create_resignation_report(bot, ctx):#, match):
    if not Priv.check_priv(ctx,Priv.ADMIN):
        return
    for m in ctx['message']:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
    gid = ctx['group_id']
    apikey = get_apikey(gid)
    global game_server
    game_server = get_GmServer(gid)
    url = f'{yobot_url}/yobot/clan/{gid}/statistics/api/?apikey={apikey}'
    
    #print(url)
    #访问yobot api获取伤害等信息
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    clanname = data['groupinfo'][0]['group_name']
    if clanname == 0:
        await bot.send(event, f'！当前没有创建公会，无法使用')
        return
    challenges: list = data['challenges']
    names: list = data['members']
    for name in names[::-1]:
        if name['qqid'] == uid:
            nickname = name['nickname']
            if nickname == 0:
                await bot.send(event, f'未加入公会或已从公会离职，无法生成报告')
                return
    for chl in challenges[::-1]:
        if chl['qqid'] != uid:
            challenges.remove(chl)
    total_chl = len(challenges)
    if total_chl == 0:
        await bot.send(event, f'没有查询到出刀数据，请出刀后再试')
        return
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_damage = 0
    for chl in challenges[::-1]:
        total_damage += chl['damage']
        times_to_boss[chl['boss_num']-1] += 1
    avg_day_damage = int(total_damage/6)
    for chl in challenges[::-1]:
        if chl['health_ramain'] != 0 and chl['is_continue'] == 0:
            damage_to_boss[chl['boss_num']-1] += chl['damage']
            truetimes_to_boss[chl['boss_num']-1] += 1
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    for chl in challenges[::-1]:
        if chl['damage'] != 0 or chl['is_continue']:
            challenges.remove(chl)
    Miss_chl = len(challenges)     
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)
    
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x()+0.1, h, f'{int(times_to_boss[i])}刀',fontdict={"size":12})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = Image.open(os.path.join(current_folder,background2))
    img.paste(bar_img1, (580,950), mask=bar_img1.split()[3])
    img.paste(bar_img2, (130,950), mask=bar_img2.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {Miss_chl}

    {avg_day_damage}
    '''
    #year = '2020'
    #month = '7'
    #constellation = '双子'
    
    add_text(img, row1, position=(380,630), textsize=35)
    add_text(img, row2, position=(833,630), textsize=35)
    add_text(img, year, position=(355,438), textsize=40)
    add_text(img, month, position=(565,438), textsize=40)
    add_text(img, pcr_constellations(month), position=(710,438), textsize=40)
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 520), textsize=40)
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30)
    add_text1(img, nickname, position=(280,365), textsize=35)

    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ctx, f'[CQ:image,file={base64_str}]')
    _lmt.start_cd(uid)