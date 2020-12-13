from hoshino import Service, R
from . import main
from . import get

sv = Service('选图生成', visible= True, enable_on_default= True, bundle='选图生成', help_='''
- [表情包帮助] 
'''.strip())

@sv.on_prefix(('选图','imgsw','IMGSW'))
async def switch_img(bot, ev):
    uid = ev.user_id
    msg = str(ev.message).strip()
    mark = await get.setQqName(uid,msg)
    if mark != None:
            img = R.img(f'image-generate/image_data/{mark}/{mark}.jpg').cqcode
            await bot.send(ev,f'表情已更换为{msg}\n{img}', at_sender=True)

@sv.on_suffix(('.jpg','.JPG'))
@sv.on_prefix(('生成表情包','imgen','IMGEN'))
async def generate_img(bot, ev):
    msg = ev.message.extract_plain_text()
    uid = ev.user_id
    await main.img(bot, ev, msg, uid)
    
@sv.on_fullmatch(('表情包帮助','imghelp'))
async def imgen_help(bot, ev):
    msg = '''
[选图 猫猫] 选择生成表情包所用的底图
[选图列表] 查看能选择的底图列表,<>内的数字为必选数字
[HelloWorld.jpg] 将.jpg前的文字作为内容来生成表情包
'''
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch(('选图列表','imgswl','IMGSWL'))
async def switch_list(bot, ev):
    msg = '''
狗妈<1~3>
熊猫<1~3>
马自立<1~2>
粽子<1~2>
吹雪<1~2>
心心
阿夸
臭鼬
好学
黑手
逗乐了
奥利给
kora
珂学家
财布
守夜冠军
恶臭
我爱你
peko
星姐
爱丽丝
猫猫
猪
猫猫猫
gvc
猫
ksm
栞栞
'''
    await bot.send(ev, msg, at_sender=True)
