from traceback import print_exc
from nonebot.message import MessageSegment, Message
from aiocqhttp.event import Event
from os import path
from hoshino.log import new_logger
from typing import Callable
import re
import random
import aiohttp
import filetype
import os

logger = new_logger('shebot')

async def download_async(url: str, save_path: str, save_name: str, suffix=None) -> None:
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            content = await resp.read()
            if not suffix: #没有指定后缀，自动识别后缀名
                try:
                    suffix = filetype.guess_mime(content).split('/')[1]
                except:
                    raise ValueError('不是有效文件类型')
            abs_path = path.join(save_path, f'{save_name}.{suffix}')
            with open(abs_path, 'wb') as f:
                f.write(content)
                return abs_path

def get_random_file(path) -> str:
    files = os.listdir(path)
    rfile = random.choice(files)
    return rfile

import hashlib
def get_str_md5(text: str) -> str:
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    md5_str = m.hexdigest()
    return md5_str

class Res:
    res_dir = path.join(path.dirname(__file__), 'modules','shebot', 'res')
    image_dir = path.join(res_dir, 'image')
    record_dir = path.join(res_dir, 'record')
    @classmethod
    def image(cls, pic_path: str) -> 'MessageSegment':
        return MessageSegment.image(f'file:///{path.join(cls.image_dir, pic_path)}')

    @classmethod
    def record(cls, rec_path) -> 'MessageSegment':
        return MessageSegment.record(f'file:///{path.join(cls.record_dir, rec_path)}')

    @classmethod
    async def save_image(cls, event: Event, folder=None) -> None:
        if not folder:
            image_path = cls.image_dir
        else:
            image_path = path.join(cls.image_dir, folder)
        if not path.isdir(image_path):
            os.mkdir(image_path)
        for i, m in enumerate(event.message):
            match = re.match('\[CQ:image.+?\]', str(m))
            if match:
                try:
                    url = re.findall(r'http.*?term=\d', str(m))[0]
                    save_name = re.findall(r'(?<=-)[^-]*?(?=/)',url)[0]
                    image = await download_async(url, image_path, save_name)
                    event.message[i] = MessageSegment.image(f'file:///{image}')
                except Exception as ex:
                    print_exc()
        event.raw_message = str(event.message)

    @classmethod
    def get_random_image(cls, folder=None) -> 'MessageSegment':
        if not folder:
            image_path = cls.image_dir
        else:
            image_path = path.join(cls.image_dir, folder)
        image_name = get_random_file(image_path)
        return MessageSegment.image(f'file:///{path.join(image_path, image_name)}')

    @classmethod
    async def image_from_url(cls, url: str, cache=True) -> 'MessageSegment':
        fname = get_str_md5(url)
        image = path.join(cls.image_dir, f'{fname}.jpg')
        if not path.exists(image) or not cache:
            image = await download_async(url, cls.image_dir, fname, 'jpg')
        return MessageSegment.image(f'file://{image}') 

from nonebot import scheduler
import datetime
import nonebot
bot = nonebot.get_bot()
def add_delay_job(task,id=None,delay_time:int=30,args=[]):
    now = datetime.datetime.now()
    job = scheduler.add_job(task,'date',id=id,run_date=now+datetime.timedelta(seconds=delay_time),misfire_grace_time=5,args=args)
    return job

def add_date_job(task,id=None,run_date=None,args=[]):
    job = scheduler.add_job(task,'date',id=id,run_date=run_date,args=args)
    return job

def add_cron_job(task,id=None,hour='*',minute='0',second='0',args=[]):
    job = scheduler.add_job(task,'cron',id=id,hour=hour,minute=minute,second=second,misfire_grace_time=5,args=args)
    return job

import json
def save_config(config:dict,path:str):
    try:
        with open(path,'w',encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        logger.error(ex)
        return False

def load_config(path):
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except Exception as ex:
        logger.error(f'exception occured when loading config in {path}  {ex}')
        logger.exception(ex)
        return {}

import asyncio
from hoshino.service import Service
async def broadcast(msg,groups=None,sv_name=None):
    bot = nonebot.get_bot()
    #当groups指定时，在groups中广播；当groups未指定，但sv_name指定，将在开启该服务的群广播
    svs = Service.get_loaded_services()
    if not groups and sv_name not in svs:
        raise ValueError(f'不存在服务 {sv_name}')
    if not groups:
        enable_groups = await svs[sv_name].get_enable_groups()
        send_groups = enable_groups.keys()
    else:
        send_groups = groups

    for gid in send_groups:
        try:
            await bot.send_group_msg(group_id=gid,message=msg)
            logger.info(f'群{gid}投递消息成功')
            await asyncio.sleep(0.5)
        except:
            logger.error(f'在群{gid}投递消息失败')

class RSS():
    def __init__(self):
        self.base_url = 'http://112.74.76.48:1200'
        self.route :str= None
        self.xml : bytes = None
        self.filter : dict = dict()
        self.filterout :dict = dict() #out为过滤掉
        '''
        filter 选出想要的内容
        filter: 过滤标题和描述
        filter_title: 过滤标题
        filter_description: 过滤描述
        filter_author: 过滤作者
        filter_time: 过滤时间，仅支持数字，单位为秒。返回指定时间范围内的内容。如果条目没有输出pubDate或者格式不正确将不会被过滤
        '''
        self.filter_case_sensitive = True #过滤是否区分大小写,默认区分大小写
        self.limit = 10 #限制最大条数，主要用于排行榜类 RSS

    async def get(self):
        url = self.base_url + self.route
        params = {}
        for key in self.filter:
            if self.filter[key]:
                params[key] = self.filter[key]
        for key in self.filterout:
            if self.filterout[key]:
                params[key] = self.filterout[key]
        params['limit'] = self.limit
        async with aiohttp.ClientSession() as session:
            async with session.get(url,params=params) as resp:
                self.xml = await resp.read()

    def parse_xml(self):
        #在实现类中编写解析xml函数
        raise NotImplementedError

from hoshino.modules.priconne.cherugo import cheru2str
def cherugo_also(func: Callable) -> Callable:
    async def deco(*args):
        bot, event, _ = tuple(args)
        await func(bot, event, _)
        raw_message = event.raw_message
        cherugo_decode = cheru2str(raw_message)
        event.raw_message = cherugo_decode
        event.message.clear()
        event.message.append(MessageSegment.text(cherugo_decode))
        await func(bot, event, _)
    return deco