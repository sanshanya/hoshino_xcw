from .nmsl_local import *

from hoshino import Service

sv = Service('text2emoji', bundle='pcr娱乐', help_='''
[抽象一下] 转换为抽象话
[我佛辣] 转换为深度抽象话
'''.strip())

@sv.on_prefix(('抽象一下','轻度抽象'))
async def emoji(bot, ev):
    text = ev.message.extract_plain_text()
    msg = text_to_emoji(text,method=0)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(('我佛辣','深度抽象'))
async def nmsl(bot, ev):
    text = ev.message.extract_plain_text()
    msg = text_to_emoji(text,method=1)
    await bot.send(ev, msg, at_sender=True)