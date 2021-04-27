import os
import random


from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment


from hoshino import R, Service, priv



sv_help = '''
xcw系列功能，自行发掘彩蛋
'''.strip()

sv = Service(
    name = 'xcw',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助xcw"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


'''-----随机发送文件夹内容①----------'''
xcw_folder_mawo = R.get('img/xcw/record/mawo/').path
xcw_folder_pa = R.get('img/xcw/image/pa/').path
xcw_folder_huhuhu = R.get('img/xcw/image/huhuhu/').path
xcw_folder_kkp = R.get('img/xcw/record/kkp/').path
xcw_folder_biantai = R.get('img/xcw/record/biantai/').path

'''-----随机发送文件夹内容②----------'''
def get_xcw_mawo():  #get
    files = os.listdir(xcw_folder_mawo)  #folder
    filename = random.choice(files)
    rec = R.get('img/xcw/record/mawo/', filename)  #folder
    return rec

def get_xcw_pa():
    files = os.listdir(xcw_folder_pa)
    filename = random.choice(files)
    rec = R.get('img/xcw/image/pa', filename)
    return rec

def get_xcw_huhuhu():
    files = os.listdir(xcw_folder_huhuhu)
    filename = random.choice(files)
    rec = R.get('img/xcw/image/huhuhu', filename)
    return rec

def get_xcw_kkp():
    files = os.listdir(xcw_folder_kkp)
    filename = random.choice(files)
    rec = R.get('img/xcw/record/kkp', filename)
    return rec

def get_xcw_biantai():
    files = os.listdir(xcw_folder_biantai)
    filename = random.choice(files)
    rec = R.get('img/xcw/record/biantai', filename)
    return rec

'''-----随机发送文件夹结束----------'''


'''=======混合文本开始==========='''      
dong_d = f'''洞洞还小你们不要~
{R.img(f"xcw/image/脸红.png").cqcode}
'''.strip()

'''=======混合文本结束==========''' 

######开始发送
'''xxxxxxx语音xxxxxxxxx'''
@sv.on_fullmatch('骂我', only_to_me=True)
async def xcw_mawo(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_xcw_mawo()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
        
@sv.on_keyword(('厉害了','666','斯国一'))
async def shigyi(bot, ev):
    if random.random() < 0.5:
        filename = '斯国一斯国一.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")

@sv.on_keyword(('kkp'))
async def kkp(bot, ev):
    file = get_xcw_kkp()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_keyword('变态', only_to_me=True)
async def biantai(bot, ev):
    if random.random() < 0.5:
        file = get_xcw_biantai()
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    else:
        await bot.send(ev, '变态~', at_sender=True)
    
'''xxxxxxx语音结束xxxxxxxxx'''


@sv.on_fullmatch(('娇喘','喘气'), only_to_me=True)
async def xcw_jiaochuan(bot, ev) -> MessageSegment:
    roll = random.random()
    if roll <= 0.05:
        filename = '喘息声.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    elif 0.05 < roll <= 0.15:
        file = get_xcw_biantai()
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    elif 0.15 < roll <= 0.4:
        filename = '叹气声.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    elif 0.4 < roll <= 0.75:
        filename = '叹气声2.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    elif 0.75 < roll <= 0.95:
        filename = '叹气声2.mp3'
        file = R.get('img/xcw/record', filename)
        try:
            rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
            await bot.send(ev, rec)
        except CQHttpError:
            sv.logger.error("发送失败")
    else:
        await bot.send(ev, '我懂了你是变态吧~', at_sender=True)
    
@sv.on_keyword('爬', only_to_me=False)
async def xcw_pa(bot, ev) -> MessageSegment:
    file = get_xcw_pa()
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_keyword('呼呼呼', only_to_me=False)
async def xcw_huhuhu(bot, ev) -> MessageSegment:
    file = get_xcw_huhuhu()
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
        
@sv.on_keyword(('0爆','0暴','零爆','零暴'))
async def xcw_0bao(bot, ev) -> MessageSegment:
    filename = '0爆.jpg'
    file = R.get('img/xcw/image', filename)
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

        
@sv.on_fullmatch('啊这', only_to_me=False)
async def az(bot, ev):
    if random.random() < 0.5:
        await bot.send(ev, R.img('xcw/image/成熟点.jpg').cqcode)
       
@sv.on_keyword(('上课了'))
async def shangke(bot, ev):
    filename = 'shangke.jpg'
    file = R.get('img/xcw/image', filename)
    try:
        rec = MessageSegment.image(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")


@sv.on_keyword(('洞洞'))
async def dongdong(bot, ev):
    if random.random() < 0.3:
        await bot.send(ev, dong_d)