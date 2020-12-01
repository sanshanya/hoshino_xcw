import os
import hoshino
import asyncio
import base64
from .nokia import generate_image
from io import BytesIO
from hoshino import Service
from PIL import Image
from hoshino.util import pic2b64
from nonebot import MessageSegment

HELP_MSG = '''/nokia <文案> | 生成一张内鬼表情包'''
sv = Service('有内鬼', bundle='pcr娱乐', help_=HELP_MSG)


@sv.on_prefix(('/nokia', '有内鬼'))
async def generate_neigui(bot, event):
    msg = event.message.extract_plain_text()
    base64_str = f'base64://{generate_image(msg)}'
    await bot.send(event, f'[CQ:image,file={base64_str}]')
