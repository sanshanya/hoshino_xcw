from io import BytesIO
import os
import aiohttp
import datetime
import calendar
import re
import base64
import json
from hoshino import Service, priv 
from hoshino.util import FreqLimiter
from hoshino.typing import CQEvent
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from PIL import Image,ImageFont,ImageDraw
import math

lmt = FreqLimiter(60)   #冷却时间60秒
bg_resign = 'resign.jpg'
bg_report = 'report.jpg'
font_path = os.path.join(os.path.dirname(__file__), 'SimHei.ttf')
constellation_name = ['？？？', '水瓶', '双鱼', '白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯']
cycle_data = {
    'cn': {
        'cycle_mode': 'days',
        'cycle_days': 28,
        'base_date': datetime.date(2020, 7, 28),  #从巨蟹座开始计算
        'base_month': 5,
        'battle_days': 6,
        'reserve_days': 0
    },
    'jp': {
        'cycle_mode': 'nature',
        'cycle_days': 0,
        'base_date': None,
        'base_month': 0,
        'battle_days': 5,
        'reserve_days': 1   #月末保留非工会战天数
    },
    'tw': {
        'cycle_mode': 'nature',
        'cycle_days': 0,
        'base_date': None,
        'base_month': 7,
        'battle_days': 6,
        'reserve_days': 1
    }
}
url_valid = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

sv_help = '''
API地址获取步骤：
网页面板-统计-获取api
- [生成会战报告 @用户 API地址] 生成会战报告
- [生成离职报告 @用户 API地址] 生成离职报告
- [设置工会api API地址] (需要管理员权限)为本群设置默认的Yobot工会API
- [查看工会api] (需要管理员权限)查看本群设置的Yobot API
- [清除工会api] 
'''.strip()

sv = Service(
    name = '会战报告',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '会战', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助会战报告"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    
# 单json文件储存全部群api会出现奇怪的bug 所以每个群使用一个独立文件
#读取群api
def load_group_api(group_id):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    if not os.path.exists(config_file):
        return ""  # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config['api_url']
    except Exception as e:
        sv.logger.error(f'Error: {e}')
    return ""

#保存群api
def save_group_api(group_id, api_url):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    try:
        with open(config_file, 'w', encoding='utf8') as f:
            json.dump(
                {
                    "api_url": api_url
                },
                f,
                ensure_ascii=False,
                indent=2)
    except Exception as e:
        sv.logger.error(f'Error: {e}')

#删除群api
def delete_group_api(group_id):
    config_file = os.path.join(os.path.dirname(__file__), 'data', f'{group_id}.json')
    if os.path.exists(config_file):
        try:
            os.remove(config_file)
        except Exception as e:
            sv.logger.error(f'Error: {e}')

#获取字符串长度（以半角字符计算）
def str_len(name):
    i = 0
    for uchar in name:
        if ord(uchar) > 255:
            i = i + 2
        else:
            i = i + 1
    return i

#获取工会战开始天数 第一天=0
#日服台服开始前返回值为负 国服为正(大于工会战持续天数)
def get_days_from_battle_start(server='cn'):
    if not server in cycle_data.keys():
        return -1
    cdata = cycle_data[server]
    today = datetime.date.today()
    #today = datetime.date(2020, 8, 31)
    month_days = calendar.monthrange(today.year,today.month)[1]
    if cdata['cycle_mode'] == 'nature': #自然月 日台服
        return today.day - (month_days - cdata['battle_days'] - cdata['reserve_days'] + 1)
    else:
        return (today - cdata['base_date']).days % cdata['cycle_days']

#获取工会战总天数
def get_battle_days(server='cn'):
    if not server in cycle_data.keys():
        return 6
    return cycle_data[server]['battle_days']

#获取工会战实际月份
def get_clanbattle_month(server='cn'):
    if not server in cycle_data.keys():
        return 0
    cdata = cycle_data[server]
    today = datetime.date.today()
    year = today.year
    month = 0
    if cdata['cycle_mode'] == 'nature': #自然月 日台服
        if get_days_from_battle_start(server) < 0: #本月还没有开始 使用上个月
            month = today.month - 1
        else: #本月工会战已开始
            month = today.month
        if month < 1:
            month = 12
            year -= 1
        return (year, month)
    else:   #天数周期循环 国服
        during_month = (today - cdata['base_date']).days // cdata['cycle_days']
        start_date = cdata['base_date'] + datetime.timedelta(days=during_month*cdata['cycle_days'])
        return (start_date.year, start_date.month)

#获取工会战星座月份
def get_constellation(server='cn'):
    if not server in cycle_data.keys():
        return constellation_name[0]    #返回？？？
    cdata = cycle_data[server]
    today = datetime.date.today()
    month = 0
    if cdata['cycle_mode'] == 'nature': #自然月 日台服
        if get_days_from_battle_start(server) < 0: #本月还没有开始 使用上个月
            month = today.month - 1
        else: #本月工会战已开始
            month = today.month
        month += cdata['base_month']
        if month < 1:
            month = 12
        elif month > 12:
          month -= 12
    else:   #天数周期循环 国服
        during_month = (today - cdata['base_date']).days // cdata['cycle_days']
        month = during_month + cdata['base_month']
        month = month % 12 + 1
    return constellation_name[month]

def add_text(img: Image,text:str,textsize:int,font=font_path,textfill='black',position:tuple=(0,0)):
    #textsize 文字大小
    #font 字体，默认微软雅黑
    #textfill 文字颜色，默认黑色
    #position 文字偏移（0,0）位置，图片左上角为起点
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img

async def send_report(bot, event, background):
    uid = None
    api_url = ""
    for m in event['message']:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
        elif m.type == 'text':
            api_url = str(m.data['text']).strip()
    if uid is None: #本人
        uid = event['user_id']
    else:   #指定对象
        if not priv.check_priv(event,priv.ADMIN):
            await bot.send(event, '查看指定用户的报告需要管理员权限', at_sender=True)
            return
    #如果没有提供api就从设置中读取
    if url_valid.match(api_url) is None:
        api_url = load_group_api(event.group_id)
    if url_valid.match(api_url) is None:
        await bot.send(event, f'API地址{api_url}错误,请提供正确的Yobot API地址', at_sender=True)
        return
    if not lmt.check(uid):
        await bot.send(event, f'报告生成器冷却中,剩余时间{round(lmt.left_time(uid))}秒', at_sender=True)
        return
    lmt.start_cd(uid)

    nickname = None
    data = None
    #访问yobot api获取伤害等信息
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
    except Exception as e:
        sv.logger.error(f'Error: {e}')
        await bot.send(event, '无法访问API，请检查yobot服务器状态', at_sender=True)
        return

    clanname = data['groupinfo'][0]['group_name']
    game_server = data['groupinfo'][0]['game_server']

    challenge_list = []

    for name in data['members']:
        if name['qqid'] == uid:
            nickname = name['nickname']
    if nickname is None:
        await bot.send(event, '该用户的工会战记录不存在', at_sender=True)
        return
    for item in data['challenges']:
        if item['qqid'] == uid:
            challenge_list.append(item)
    
    total_challenge = 0 #总出刀数
    total_damage = 0    #总伤害
    lost_challenge = 0  #掉刀
    forget_challenge = 0    #漏刀
    damage_to_boss = [0 for i in range(5)]  #各boss总伤害
    times_to_boss = [0 for i in range(5)]   #各boss出刀数
    truetimes_to_boss = [0 for i in range(5)]   #各boss出刀数 不包括尾刀
    avg_boss_damage = [0 for i in range(5)] #boss均伤
    attendance_rate = 0 #出勤率
    battle_days = get_battle_days(game_server) #会战天数
    #计算当前为工会战第几天 取值范围1~battle_days
    current_days = get_days_from_battle_start(game_server) 
    if current_days < 0 or current_days >= battle_days:
        current_days = battle_days
    else: #0 ~ battle_days-1
        current_days += 1

    for challenge in challenge_list:
        total_damage += challenge['damage']
        times_to_boss[challenge['boss_num']-1] += 1
        if not challenge['is_continue']:
            damage_to_boss[challenge['boss_num']-1] += challenge['damage']  #尾刀伤害不计入单boss总伤害，防止avg异常
            truetimes_to_boss[challenge['boss_num']-1] += 1
            total_challenge += 1
            if challenge['damage'] == 0:    #掉刀
                lost_challenge += 1
    if current_days * 3 < total_challenge: #如果会战排期改变 修正天数数据
        current_days =  math.ceil(float(total_challenge) / 3)
    avg_day_damage = int(total_damage/current_days)
    forget_challenge = current_days * 3 - total_challenge
    if forget_challenge < 0:    #修正会战天数临时增加出现的负数漏刀
        forget_challenge = 0
    attendance_rate = round(total_challenge / (current_days * 3) * 100)

    for i in range(0,5):
        if truetimes_to_boss[i] > 0:    #排除没有出刀或只打尾刀的boss
            avg_boss_damage[i] = damage_to_boss[i] // truetimes_to_boss[i]    #尾刀不计入均伤和出刀图表
    
    #设置中文字体
    font_manager.fontManager.addfont(font_path)
    plt.rcParams['font.family']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

    x = [f'{x}王' for x in range(1,6)]
    y = truetimes_to_boss
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
        plt.text(rec.get_x()+0.1, h, f'{int(truetimes_to_boss[i])}刀',fontdict={"size":12})
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
    img = Image.open(os.path.join(current_folder,background))
    img.paste(bar_img1, (580,950), mask=bar_img1.split()[3])
    img.paste(bar_img2, (130,950), mask=bar_img2.split()[3])

    #添加文字到img
    row1 = f'''
    {total_challenge}

    {forget_challenge}

    {total_damage // 10000}万
    '''
    row2 = f'''
    {attendance_rate}%

    {lost_challenge}

    {avg_day_damage // 10000}万
    '''
    
    add_text(img, row1, position=(380,630), textsize=42)
    add_text(img, row2, position=(833,630), textsize=42)

    year, month = get_clanbattle_month(game_server)
    add_text(img, str(year), position=(355,445), textsize=40)
    add_text(img, str(month), position=(565,445), textsize=40)
    add_text(img, get_constellation(game_server), position=(710,445), textsize=40)

    # 公会名称区域 (300,520) (600, 560) width:300 height:40
    # 使用40号字体，最长可放置20个半角字符，如果超长则自动缩减字体并移动坐标
    length = str_len(clanname)
    font_size = 600 // length
    if font_size > 40:
        font_size = 40
    x = 450 - length * font_size // 4
    y = 520 + (40 - font_size) // 2
    add_text(img, clanname, position=(x, y), textsize=font_size) #公会名

    add_text(img, nickname, position=(280,367), textsize=40, textfill='white',)   #角色名
    #输出
    buf = BytesIO()
    img.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(event, f'[CQ:image,file={base64_str}]', at_sender=True)
    plt.close('all')

@sv.on_prefix('生成离职报告')
async def create_resign_report(bot, event: CQEvent):
    await send_report(bot, event, bg_resign)

@sv.on_prefix('生成会战报告')
async def create_clanbattle_report(bot, event: CQEvent):
    await send_report(bot, event, bg_report)

@sv.on_prefix(('设置工会api', '设置公会api'))
async def set_clanbattle_api(bot, event: CQEvent):
    if not priv.check_priv(event,priv.ADMIN):
        await bot.send(event, '该操作需要管理员权限', at_sender=True)
        return
    api_url = event.message.extract_plain_text().strip()
    if url_valid.match(api_url) is None:
        await bot.send(event, f'API地址{api_url}无效', at_sender=True)
        return
    save_group_api(event.group_id, api_url)
    await bot.send(event, f'本群工会API已设置为 {api_url}', at_sender=True)

@sv.on_fullmatch(('查看工会api', '查看公会api'))
async def get_clanbattle_api(bot, event: CQEvent):
    if not priv.check_priv(event,priv.ADMIN):
        await bot.send(event, '该操作需要管理员权限', at_sender=True)
        return
    api_url = load_group_api(event.group_id)
    await bot.send(event, f'本群工会API为 {api_url}', at_sender=True)

@sv.on_fullmatch(('清除工会api', '清除公会api'))
async def delete_clanbattle_api(bot, event: CQEvent):
    if not priv.check_priv(event,priv.ADMIN):
        await bot.send(event, '该操作需要管理员权限', at_sender=True)
        return
    delete_group_api(event.group_id)
    await bot.send(event, '本群工会API已清除', at_sender=True)