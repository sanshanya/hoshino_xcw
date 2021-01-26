import os
import hoshino
import asyncio
import base64
from .nokia import generate_image
from io import BytesIO
from hoshino import Service, priv
from PIL import Image
from hoshino.util import pic2b64
from nonebot import MessageSegment


sv_help = '''
- [有内鬼 文案]  生成一张内鬼表情包
'''.strip()

sv = Service(
    name = '有内鬼',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助有内鬼"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

@sv.on_prefix(('/nokia', '有内鬼'))
async def generate_neigui(bot, event):
    msg = event.message.extract_plain_text()
    base64_str = f'base64://{generate_image(msg)}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')
