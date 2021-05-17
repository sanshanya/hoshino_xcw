import requests
from hoshino import Service,priv
from nonebot import MessageSegment
from nonebot.exceptions import CQHttpError
import asyncio
from os import listdir
from PIL import Image
import cv2
import random

sv_help = f'''
长色图demo
写到一半不想写了
30与63行为涩图库路径
57行左右的是go-cqhttp的images
快来个人接手
'''.strip()

sv = Service(
    name = '长色图',
    use_priv = priv.NORMAL,
    manage_priv = priv.ADMIN,
    visible = True,
    enable_on_default = True,
    bundle = '通用',
    help_ = sv_help
    )

    

def setu_make(group_id):
    ims = [Image.open('C:/res/img/setu_mix/lolicon/%s' % fn) for fn in listdir('C:/res/img/setu_mix/lolicon') if fn.endswith('.jpg')]
    ims = random.sample(ims, 10)
    ims_size = [list(im.size) for im in ims]
    middle_width = sorted(ims_size, key=lambda im: im[0])[int(len(ims_size)/2)][0]  # 中位数宽度
    ims = [im for im in ims if im.size[0] > middle_width/2]  # 过滤宽度过小的无效图片

    # 过滤后重新计算
    ims_size = [list(im.size) for im in ims]
    middle_width = sorted(ims_size, key=lambda im: im[0])[int(len(ims_size)/2)][0]  # 中位数宽度
    ims = [im for im in ims if im.size[0] > middle_width/2]  # 过滤宽度过小的无效图片

    # 计算相对长图目标宽度尺寸
    for i in range(len(ims_size)):
        rate = middle_width/ims_size[i][0]
        ims_size[i][0] = middle_width
        ims_size[i][1] = int(rate*ims_size[i][1])
    sum_height = sum([im[1] for im in ims_size])
    # 创建空白长图
    result = Image.new(ims[0].mode, (middle_width, sum_height))
    # 拼接
    top = 0
    for i, im in enumerate(ims):
        mew_im = im.resize(ims_size[i], Image.ANTIALIAS)  # 等比缩放
        result.paste(mew_im, box=(0, top))
        top += ims_size[i][1]
    # 保存
    result.save(f'C:/XCW/go-cqhttp/data/images/{group_id}1.png')
    img=cv2.imread(f"C:/XCW/go-cqhttp/data/images/{group_id}1.png",1)
    cv2.imwrite(f"C:/XCW/go-cqhttp/data/images/{group_id}.jpg",img,[cv2.IMWRITE_JPEG_QUALITY,50]) # 压缩jpg为有损，质量为50
    str1 = f'{group_id}.jpg'
    return str1
    
def setu_r18_make(group_id):
    ims = [Image.open('C:/res/img/setu_mix/lolicon_r18/%s' % fn) for fn in listdir('C:/res/img/setu_mix/lolicon_r18') if fn.endswith('.jpg')]
    ims = random.sample(ims, 15)
    ims_size = [list(im.size) for im in ims]
    middle_width = sorted(ims_size, key=lambda im: im[0])[int(len(ims_size)/2)][0]  # 中位数宽度
    ims = [im for im in ims if im.size[0] > middle_width/2]  # 过滤宽度过小的无效图片

    # 过滤后重新计算
    ims_size = [list(im.size) for im in ims]
    middle_width = sorted(ims_size, key=lambda im: im[0])[int(len(ims_size)/2)][0]  # 中位数宽度
    ims = [im for im in ims if im.size[0] > middle_width/2]  # 过滤宽度过小的无效图片

    # 计算相对长图目标宽度尺寸
    for i in range(len(ims_size)):
        rate = middle_width/ims_size[i][0]
        ims_size[i][0] = middle_width
        ims_size[i][1] = int(rate*ims_size[i][1])
    sum_height = sum([im[1] for im in ims_size])
    # 创建空白长图
    result = Image.new(ims[0].mode, (middle_width, sum_height))
    # 拼接
    top = 0
    for i, im in enumerate(ims):
        mew_im = im.resize(ims_size[i], Image.ANTIALIAS)  # 等比缩放
        result.paste(mew_im, box=(0, top))
        top += ims_size[i][1]
    # 保存
    result.save(f'C:/XCW/go-cqhttp/data/images/{group_id}12.png')
    img=cv2.imread(f"C:/XCW/go-cqhttp/data/images/{group_id}12.png",1)
    cv2.imwrite(f"C:/XCW/go-cqhttp/data/images/{group_id}123.jpg",img,[cv2.IMWRITE_JPEG_QUALITY,50]) # 压缩jpg为有损，质量为80
    str2 = f'{group_id}123.jpg'
    return str2
    
@sv.on_fullmatch(["长长的"])
async def setu(bot, ev):
    str1 = setu_make(ev.group_id)
    await bot.send(ev, f'[CQ:image,file={str1}]')
    
