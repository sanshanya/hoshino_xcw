import re
import aiohttp
import asyncio
import feedparser
from PIL import Image
from io import BytesIO
import math
import base64
import hoshino
import traceback
import os
import json
import time


rss_news = {}

data = {
    'rsshub': 'https://rsshub.di.he.cn',
    'proxy': '',
    'proxy_urls': [],
    'last_time': {},
    'group_rss': {},
    'group_mode': {},
}

HELP_MSG = '''rss订阅
rss list : 查看订阅列表
rss add rss地址 : 添加rss订阅
rss addb up主id : 添加b站up主订阅
rss addr route : 添加rsshub route订阅
rss remove 序号 : 删除订阅列表指定项
rss mode 0/1 : 设置消息模式 标准/简略
详细说明见项目主页: https://github.com/zyujs/rss
'''

sv = hoshino.Service('rss', bundle='pcr订阅', help_= HELP_MSG)

def save_data():
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

def load_data():
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    if not os.path.exists(path):
        save_data()
        return
    try:
        with open(path, encoding='utf8') as f:
            d = json.load(f)
            if 'rsshub' in d:
                if d['rsshub'][-1] == '/':
                    d['rsshub'] = d['rsshub'][:-1]
                data['rsshub'] = d['rsshub']
            if 'last_time' in d:
                data['last_time'] = d['last_time']
            if 'group_rss' in d:
                data['group_rss'] = d['group_rss']
            if 'group_mode' in d:
                data['group_mode'] = d['group_mode']
            if 'proxy' in d:
                data['proxy'] = d['proxy']
            if 'proxy_urls' in d:
                data['proxy_urls'] = d['proxy_urls']
    except:
        traceback.print_exc()
    global default_rss

load_data()

default_rss = [
    data['rsshub'] + '/bilibili/user/dynamic/353840826',    #pcr官方号
    ]

async def query_data(url, proxy=''):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=proxy) as resp:
                return await resp.read()
    except:
        return None

def get_image_url(desc):
    imgs = re.findall('<img src="(.+?)".+?>', desc)
    return imgs

def remove_html(content):
    #移除html标签
    p = re.compile('<[^>]+>')
    content = p.sub("", content)
    return content

def remove_lf(content):
    text = ''
    for line in content.splitlines():
        line =  line.strip()
        if line:
            text += line + '\n'
    text = text.rstrip()
    return text

async def generate_image(url_list):
    raw_images = []
    num = 0
    for url in url_list:
        proxy = ''
        for purl in data['proxy_urls']:
            if purl in url:
                proxy = data['proxy']
        image = await query_data(url, proxy)
        if image:
            try:
                im = Image.open(BytesIO(image))
                im = im.convert("RGBA")
                raw_images.append(im)
                num += 1
            except:
                pass
        if num >= 9:
            break

    if num == 0:
        return None
    elif num == 1:
        io = BytesIO()
        raw_images[0].save(io, 'png')
        return io.getvalue()

    dest_img = None
    box_size = 300
    row = 3
    border = 5
    width = 0
    width = 0
    if num == 3 or num >= 5:    #3列
        width = 900 + border * 2
        height = math.ceil(num / 3) * (300 + border) - border
    else: #2列
        box_size = 400
        row = 2
        width = 800 + border
        height = math.ceil(num / 2) * (400 + border) - border
    dest_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))

    for i in range(num):
        im = raw_images[i]
        if im:
            w, h = im.size
            if w > h:
                x0 = (w // 2) - (h // 2)
                x1 = x0 + h
                im = im.crop((x0, 0, x1, h))
            elif h > w:
                y0 = (h // 2) - (w // 2)
                y1 = y0 + w 
                im = im.crop((0, y0, w, y1))
            im = im.resize((box_size, box_size),Image.ANTIALIAS)
            x = (i % row) * (box_size + border)
            y = (i // row) * (box_size + border)
            dest_img.paste(im, (x, y))
    io = BytesIO()
    dest_img.save(io, 'png')
    return io.getvalue()

def get_published_time(item):
    time_t = 0
    if 'published_parsed' in item:
        time_t = time.mktime(item['published_parsed'])
    if 'updated_parsed' in item:
        time_t = time.mktime(item['updated_parsed'])
    return time_t

def get_latest_time(item_list):
    last_time = 0
    for item in item_list:
        time = get_published_time(item)
        if time > last_time:
            last_time = time
    return last_time

def check_title_in_content(title, content):
    title = title[:len(title)//2]
    title = title.replace('\n', '').replace('\r', '').replace(' ', '')
    content = content.replace('\n', '').replace('\r', '').replace(' ', '')
    if title in content:
        return True
    return False
    

async def get_rss_news(rss_url):
    news_list = []
    proxy = ''
    for purl in data['proxy_urls']:
        if purl in rss_url:
            proxy = data['proxy']
    res = await query_data(rss_url, proxy)
    if not res:
        return news_list
    feed = feedparser.parse(res)
    if feed['bozo'] != 0:
        sv.logger.info(f'rss解析失败 {rss_url}')
        return news_list
    if len(feed['entries']) == 0:
        return news_list
    if rss_url not in data['last_time']:
        sv.logger.info(f'rss初始化 {rss_url}')
        data['last_time'][rss_url] = get_latest_time(feed['entries'])
        return news_list

    last_time = data['last_time'][rss_url]

    for item in feed["entries"]:
        if get_published_time(item) > last_time:
            summary = item['summary']
            #移除转发信息
            i = summary.find('//转发自')
            if i > 0:
                summary = summary[:i]
            news = {
                'feed_title': feed['feed']['title'],
                'title': item['title'],
                'content': remove_html(summary),
                'id': item['id'],
                'image': await generate_image(get_image_url(summary)),
                }
            news_list.append(news)

    data['last_time'][rss_url] = get_latest_time(feed['entries'])
    return news_list

async def refresh_all_rss():
    for item in default_rss:
        if item not in rss_news:
            rss_news[item] = []
    for group_rss in data['group_rss'].values():
        for rss_url in group_rss:
            if rss_url not in rss_news:
                rss_news[rss_url] = []
    #删除没有引用的项目的推送进度
    for rss_url in list(data['last_time'].keys()):
        if rss_url not in rss_news:
            data['last_time'].pop(rss_url)
    for rss_url in rss_news.keys():
        rss_news[rss_url] = await get_rss_news(rss_url)
    save_data()

def format_msg(news):
    msg = f"{news['feed_title']}更新:\n{news['id']}"
    if not check_title_in_content(news['title'], news['content']):
        msg += f"\n{news['title']}"
    msg += f"\n----------\n{remove_lf(news['content'])}"
    if news['image']:
        base64_str = f"base64://{base64.b64encode(news['image']).decode()}"
        msg += f'[CQ:image,file={base64_str}]'
    return msg

def format_brief_msg(news):
    msg = f"{news['feed_title']}更新:\n{news['id']}"
    msg += f"\n----------\n{news['title']}"
    return msg

async def group_process():
    bot = hoshino.get_bot()
    groups = await sv.get_enable_groups()
    await refresh_all_rss()

    for gid in groups.keys():
        rss_list = default_rss
        if str(gid) in data['group_rss']:
            rss_list = data['group_rss'][str(gid)]
        else:
            data['group_rss'][str(gid)] = default_rss
        for rss_url in rss_list:
            if rss_url in rss_news:
                news_list = rss_news[rss_url]
                for news in reversed(news_list):
                    msg = None
                    if str(gid) in data['group_mode'] and data['group_mode'][str(gid)] == 1:
                        msg = format_brief_msg(news)
                    else:
                        msg = format_msg(news)
                    try:
                        await bot.send_group_msg(group_id=gid, message=msg)
                    except:
                        sv.logger.info(f'群 {gid} 推送失败')
                await asyncio.sleep(1)

async def rss_add(group_id, rss_url):
    group_id = str(group_id)
    proxy = ''
    for purl in data['proxy_urls']:
        if purl in rss_url:
            proxy = data['proxy']
    res = await query_data(rss_url, proxy)
    feed = feedparser.parse(res)
    if feed['bozo'] != 0:
        return f'无法解析rss源:{rss_url}'
        
    if group_id not in data['group_rss']:
        data['group_rss'][group_id] = default_rss
    if rss_url not in set(data['group_rss'][group_id]):
        data['group_rss'][group_id].append(rss_url)
    else:
        return '订阅列表中已存在该项目'
    save_data()
    return '添加成功'

def rss_remove(group_id, i):
    group_id = str(group_id)
    if group_id not in data['group_rss']:
        data['group_rss'][group_id] = default_rss
    if i >= len(data['group_rss'][group_id]):
        return '序号超出范围'
    data['group_rss'][group_id].pop(i)
    save_data()
    return '删除成功\n当前' + rss_get_list(group_id)

def rss_get_list(group_id):
    group_id = str(group_id)
    if group_id not in data['group_rss']:
        data['group_rss'][group_id] = default_rss
    msg = '订阅列表:'
    num = len(data['group_rss'][group_id])
    for i in range(num): 
        url = data['group_rss'][group_id][i]
        url = re.sub(r'http[s]*?://.*?/', '/', url)
        msg += f"\n{i}. {url}"
    if num == 0:
        msg += "\n空"
    return msg

def rss_set_mode(group_id, mode):
    group_id = str(group_id)
    mode = int(mode)
    if mode > 0:
        data['group_mode'][group_id] = 1
        msg = '已设置为简略模式'
    else:
        data['group_mode'][group_id] = 0
        msg = '已设置为标准模式'
    save_data()
    return msg

@sv.on_prefix('rss')
async def rss_cmd(bot, ev):
    msg = ''
    group_id = ev.group_id
    args = ev.message.extract_plain_text().split()
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.ADMIN)

    if len(args) == 0:
        msg = HELP_MSG
    elif args[0] == 'help':
        msg = HELP_MSG
    elif args[0] == 'add':
        if not is_admin:
            msg = '权限不足'
        elif len(args) >= 2:
            msg = await rss_add(group_id, args[1])
        else:
            msg = '需要附带rss地址'
    elif args[0] == 'addb' or  args[0] == 'add-bilibili':
        if not is_admin:
            msg = '权限不足'
        elif len(args) >= 2 and args[1].isdigit():
            rss_url = data['rsshub'] + '/bilibili/user/dynamic/' + str(args[1])
            msg = await rss_add(group_id, rss_url)
        else:
            msg = '需要附带up主id'
    elif args[0] == 'addr' or  args[0] == 'add-route':
        if not is_admin:
            msg = '权限不足'
        elif len(args) >= 2:
            rss_url = data['rsshub'] + args[1]
            msg = await rss_add(group_id, rss_url)
        else:
            msg = '需要提供route参数'
        pass
    elif args[0] == 'remove' or args[0] == 'rm':
        if not is_admin:
            msg = '权限不足'
        elif len(args) >= 2 and args[1].isdigit():
            msg = rss_remove(group_id, int(args[1]))
        else:
            msg = '需要提供要删除rss订阅的序号'
    elif args[0] == 'list' or args[0] == 'ls':
        msg = rss_get_list(group_id)
    elif args[0] == 'mode':
        if not is_admin:
            msg = '权限不足'
        elif len(args) >= 2 and args[1].isdigit():
            msg = rss_set_mode(group_id, args[1])
        else:
            msg = '需要附带模式(0/1)'
    else:
        msg = '参数错误'
    await bot.send(ev, msg)

@sv.scheduled_job('interval', minutes=5)
async def job():
    await group_process()
