# -*- coding: UTF-8 -*-
import asyncio
import json
import os
import re
import uuid
from io import BytesIO
import codecs
import emoji
import feedparser
import requests
from PIL import Image
from googletrans import Translator
from nonebot.log import logger
from pyquery import PyQuery as pq
import numpy as np
from PIL import Image
import base64
from hoshino.util import pic2b64
from nonebot import MessageSegment
from .config import *

# 存储目录
file_path = abs_path

async def getRSS(rss):  # 链接，订阅名
    d = ""
    try:
        r = requests.get(rss.geturl(), timeout=30)
        d = feedparser.parse(r.content)
    except:
        logger.error("抓取订阅 {} 的 RSS 失败".format(rss.url))

    # 检查是否存在rss记录
    if os.path.isfile(file_path + (rss.url + '.json')):
        change = checkUpdate(d, readRss(rss.url))  # 检查更新
        if len(change) > 0:
            writeRss(rss.url, d)  # 写入文件
            msg_list = []
            for item in change:
                msg = '【' + d.feed.title + '】更新了!\n----------------------\n'
                # 处理item['summary']只有图片的情况
                text = re.sub('<video.+?><\/video>|<img.+?>', '', item['summary'])
                text = re.sub('<br>', '', text)
                msg = msg + '标题：' + item['title'] + '\n'
                temp = await checkstr(item['summary'])
                if temp:
                    msg = msg + '内容：' + temp + '\n'

                str_link = re.sub('member_illust.php\?mode=medium&illust_id=', 'i/', item['link'])
                msg = msg + '原链接：' + str_link + '\n'
                msg_list.append(msg)
            return msg_list
    else:
        writeRss(rss.url, d)
        return []

# 下载图片
async def dowimg(url: str):
    zip_size = 3072
    try:
        img_path = file_path + 'imgs/'
        if not os.path.isdir(img_path):
            logger.info(str(img_path) + '文件夹不存在，已重新创建')
            os.makedirs(img_path)  # 创建目录
        file_suffix = os.path.splitext(url)  # 返回列表[路径/文件名，文件后缀]
        name = str(uuid.uuid4())
        
        try:
            pic = requests.get(url)
            # 大小控制，图片压缩
            if (float(len(pic.content) / 1024) > float(zip_size)):
                filename = await zipPic(pic.content, name)
            else:
                if len(file_suffix[1]) > 0:
                    filename = name + file_suffix[1]
                elif pic.headers['Content-Type'] == 'image/jpeg':
                    filename = name + '.jpg'
                elif pic.headers['Content-Type'] == 'image/png':
                    filename = name + '.png'
                else:
                    filename = name + '.jpg'
                with codecs.open(str(img_path + filename), "wb") as dump_f:
                    dump_f.write(pic.content)

            imgs_name = img_path + filename
            if len(imgs_name) > 0:
                # imgs_name = os.getcwd() + re.sub(r'\./|\\', r'/', imgs_name)
                imgs_name = re.sub(r'\./|\\', r'/', imgs_name)
            return imgs_name
            
        except:
            logger.error('图片下载失败 2')
            return ''
    except:
        logger.error('图片下载失败 1')
        return ''


async def zipPic(content, name):
    zip_size = 3072
    img_path = file_path + 'imgs/'
    # 打开一个jpg/png图像文件，注意是当前路径:
    im = Image.open(BytesIO(content))
    # 获得图像尺寸:
    w, h = im.size
    logger.info('Original image size: %sx%s' % (w, h))
    # 算出缩小比
    Proportion = int(len(content) / (float(zip_size) * 1024))
    logger.info('算出的缩小比:' + str(Proportion))
    # 缩放
    im.thumbnail((w // Proportion, h // Proportion))
    logger.info('Resize image to: %sx%s' % (w // Proportion, h // Proportion))
    # 把缩放后的图像用jpeg格式保存:
    try:
        im.save(img_path + name + '.jpg', 'jpeg')
        return name + '.jpg'
    except:
        im.save(img_path + name + '.png', 'png')
        return name + '.png'


# 处理正文
async def checkstr(rss_str: str):
    # 去掉换行
    rss_str = re.sub('\n', '', rss_str)

    doc_rss = pq(rss_str)
    rss_str = str(doc_rss)

    # 处理一些标签
    rss_str = re.sub('<br/><br/>|<br><br>|<br>|<br/>', '\n', rss_str)
    rss_str = re.sub('<span>|<span.+?\">|</span>', '', rss_str)
    rss_str = re.sub('<pre.+?\">|</pre>', '', rss_str)
    rss_str = re.sub('<p>|<p.+?\">|</p>|<b>|<b.+?\">|</b>', '', rss_str)
    rss_str = re.sub('<div>|<div.+?\">|</div>', '', rss_str)
    rss_str = re.sub('<div>|<div.+?\">|</div>', '', rss_str)
    rss_str = re.sub('<iframe.+?\"/>', '', rss_str)
    rss_str = re.sub('<i.+?\">|<i>|</i>', '', rss_str)
    rss_str = re.sub('<code>|</code>|<ul>|</ul>', '', rss_str)
    # 解决 issue #3
    rss_str = re.sub('<dd.+?\">|<dd>|</dd>', '', rss_str)
    rss_str = re.sub('<dl.+?\">|<dl>|</dl>', '', rss_str)
    rss_str = re.sub('<dt.+?\">|<dt>|</dt>', '', rss_str)

    # <a> 标签处理
    doc_a = doc_rss('a')
    for a in doc_a.items():
        if str(a.text()) != a.attr("href"):
            rss_str = re.sub(re.escape(str(a)), str(a.text()) + ':' + (a.attr("href")) + '\n', rss_str)
        else:
            rss_str = re.sub(re.escape(str(a)), (a.attr("href")) + '\n', rss_str)

    # 删除未解析成功的 a 标签
    rss_str = re.sub('<a.+?\">|<a>|</a>', '', rss_str)

    # 处理图片
    doc_img = doc_rss('img')
    if not doc_img:
        logger.info("没有图片，pass")
        return
    for img in doc_img.items():
        img_path = await dowimg(img.attr("src"))
        if len(img_path) > 0:
            rss_str = re.sub(re.escape(str(img)), str(MessageSegment.image(pic2b64(Image.open(img_path)))), rss_str)
        else:
            rss_str = re.sub(re.escape(str(img)), r'\n图片走丢啦！\n', rss_str, re.S)

    # 处理视频
    doc_video = doc_rss('video')
    for video in doc_video.items():
        img_path = await dowimg(video.attr("poster"))
        if len(img_path) > 0:
            rss_str = re.sub(re.escape(str(video)), '视频封面：' + str(MessageSegment.image(pic2b64(Image.open(img_path)))), rss_str)
        else:
            rss_str = re.sub(re.escape(str(video)), r'视频封面：\n图片走丢啦！\n', rss_str)

    return rss_str


# 检查更新
def checkUpdate(new, old) -> list:
    try:
        a = new['entries']
    except:
        a = new.entries
    b = old['entries']
    c = []

    for i in range(2):
        count = 0
        for j in b:
            try:
                if a[i]['id'] == j['id']:
                    count = 1
            except:
                if a[i]['link'] == j['link']:
                    count = 1
        if count == 0:
            c.append(a[i])
    return c


# 读取记录
def readRss(url):
    with codecs.open(file_path + (url + ".json"), 'r', encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
    return load_dict

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
            
# 写入记录
def writeRss(url, msg):
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    with codecs.open(file_path + url + ".json", 'w', encoding='utf-8') as dump_f:
        dump_f.write(json.dumps(msg, sort_keys=True, indent=4, cls=MyEncoder))
