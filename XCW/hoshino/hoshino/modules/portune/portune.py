# -*- coding: utf-8 -*-

try:
    import ujson
except:
    import json as ujson
import re
import random
import os
import aiofiles
import hoshino
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service
from hoshino.util import pic2b64
from hoshino.typing import *
from PIL import Image, ImageSequence, ImageDraw, ImageFont


sv_help = '''
[抽签|人品|运势|抽镜华签]
随机角色/指定镜华预测今日运势
准确率高达233.3333%！
'''.strip()
#帮助文本
sv = Service('portune', help_=sv_help, bundle='pcr娱乐')

lmt = DailyNumberLimiter(1)
#设置每日抽签的次数，默认为1
BOT_NICKNAME = hoshino.config.NICKNAME
#设置bot的昵称，at，qq=xxxxxxxx处为bot的QQ号，触发命令为“凯露(bot昵称)抽签”or“抽凯露签”
absPath = hoshino.config.RES_DIR
#也可以直接填写为res文件夹所在位置，例：absPath = "C:/res/"

async def readJson(p):
    if not os.path.exists(p):
        print('failure no json exsit')
        return 'FAILURE'
    async with aiofiles.open(p, 'r', encoding='utf-8') as f:
        content = await f.read()
    content = ujson.loads(content)
    return content


async def checkFolder(path):
    dirPath = path[:path.rfind('/')]
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)


@sv.on_rex(r'.*(抽签|人品|运势|抽镜华签|抽小仓唯签).*')
async def portune(bot, ev):
    arg = str(ev.raw_message)
    rex = re.compile(BOT_NICKNAME)
    m = rex.search(arg)
    if m:
        uid = ev.user_id
        if not lmt.check(uid):
                await bot.finish(ev, f'你今天已经抽过签了，欢迎明天再来~', at_sender=True)
        lmt.increase(uid)

        rex2 = re.compile(r'抽镜华签|抽小仓唯签')
        if rex2.search(arg):
            model = 'XCW'
        else:
            model = 'DEFAULT'
        cqPath = await drawing(model)
        print(cqPath)
        await bot.send(ev, f'{R.img(cqPath).cqcode}', at_sender=True)





async def drawing(model):
    fontPath = {
        'title': absPath + 'img/portunedata/font/Mamelon.otf',
        'text': absPath + 'img/portunedata/font/sakura.ttf',
    }
    imgPath = await randomBasemap()
    if model == 'XCW':
        imgPath = absPath + 'img/portunedata/imgbase/frame_27.jpg'
    charaid = imgPath.lstrip(absPath + 'img/portunedata/imgbase/frame_')
    charaid = charaid.rstrip('.jpg')
    img = Image.open(imgPath)
    # Draw title
    draw = ImageDraw.Draw(img)
    text = await copywriting(charaid)
    title = await getTitle(text)
    text = text['content']
    font_size = 45
    color = '#F5F5F5'
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(fontPath['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                title, fill=color,font=ttfront)
    # Text rendering
    font_size = 25
    color = '#323232'
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(fontPath['text'], font_size)
    result = await decrement(text)
    if not result[0]:
        return 
    textVertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        textVertical = await vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 + 
                (result[0] - 1) * 4 - i * (font_size + 4))
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), textVertical, fill = color, font = ttfront)
    # Save
    outPath = await exportFilePath(imgPath)
    img.save(outPath)
    cqPath = outPath.replace(absPath + 'img/portunedata', 'portunedata')
    return cqPath

async def exportFilePath(originalFilePath):
    outPath = originalFilePath.replace('/imgbase/', '/out/')
    await checkFolder(outPath)
    return outPath

async def randomBasemap():
    p = absPath + 'img/portunedata/imgbase'
    return p + '/' + random.choice(os.listdir(p))

async def copywriting(charaid):
    p = absPath + 'img/portunedata/fortune/copywriting.json'
    content = await readJson(p)
    for i in content['copywriting']:
        if charaid in i['charaid']:
            typewords = i['type']
            return random.choice(typewords)
    raise Exception('Configuration file error')

async def getTitle(structure):
    p = absPath + 'img/portunedata/fortune/goodLuck.json'
    content = await readJson(p)
    for i in content['types_of']:
        if i['good-luck'] == structure['good-luck']:
            return i['name']
    raise Exception('Configuration file error')

async def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    numberOfSlices = 1
    while length > cardinality:
        numberOfSlices += 1
        length -= cardinality
    result.append(numberOfSlices)
    # Optimize for two columns
    space = ' '
    length = len(text)
    if numberOfSlices == 2:
        if length % 2 == 0:
            # even
            fillIn = space * int(9 - length / 2)
            return [numberOfSlices, text[:int(length / 2)] + fillIn, fillIn + text[int(length / 2):]]
        else:
            # odd number
            fillIn = space * int(9 - (length + 1) / 2)
            return [numberOfSlices, text[:int((length + 1) / 2)] + fillIn,
                                    fillIn + space + text[int((length + 1) / 2):]]
    for i in range(0, numberOfSlices):
        if i == numberOfSlices - 1 or numberOfSlices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality:(i + 1) * cardinality])
    return result

async def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)