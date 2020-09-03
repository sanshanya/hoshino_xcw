# -*- coding: UTF-8 -*-
from hoshino import Service
from aiocqhttp.exceptions import Error as CQHttpError
from . import main
from . import get
import os
from nonebot import MessageSegment
from hoshino.util import pic2b64
from PIL import Image
sv = Service('image')

absPath = "C:/XCW/hoshino/hoshino/modules/image"

@sv.on_fullmatch('img list')
async def list(bot, ev):
    msg = str(ev["raw_message"])
    qq = ev["user_id"]
    qun = ev["group_id"]
    await bot.send(ev, MessageSegment.image(pic2b64(Image.open(absPath + "list.jpg"))))

@sv.on_prefix('img')
async def changeImg(bot, ev):
    msg = str(ev["raw_message"])
    qq = ev["user_id"]
    qun = ev["group_id"]
    mark = await get.setQqName(qq,msg)
    if mark == 1:
        msg = msg.split(" ")[1]
        qun = ev["group_id"]
        msg = str(qq) + "表情更换为" + msg
        await bot.send(ev, msg)

@sv.on_suffix('.jpg')
async def sendImg(bot, ev):
    msg = str(ev["raw_message"])
    if msg.find("CQ:")==-1:
        qq = ev["user_id"]
        qun = ev["group_id"]
        msg = msg[0:msg.find(".")]
        qun = ev["group_id"]
        picPath = await main.img(msg,qq,qun)
        await bot.send(ev, MessageSegment.image(pic2b64(Image.open(picPath))))
