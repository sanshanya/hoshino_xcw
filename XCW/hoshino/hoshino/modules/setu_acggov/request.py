import os
import datetime
import random
import string
import aiohttp
import asyncio
import traceback
import sys
import io
from PIL import Image
from .config import *

headers = {
    'token': APIKEY,
    'referer': 'https://www.acg-gov.com/'
    }

ranking_list = {}


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#读取排行榜
async def query_ranking(date: str, page: int) -> dict:
    if date not in ranking_list:
        ranking_list[date] = {}
    if page in ranking_list[date]:
        return ranking_list[date][page]
    url = f'https://api.acg-gov.com/public/ranking?ranking_type=illust&mode={MODE}&date={date}&per_page={PER_PAGE}&page={page+1}'
    data = {}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                data = await resp.json(content_type='application/json')
                ranking_list[date][page] = data
    except Exception as e:
        traceback.print_exc()
        return {}
    return data

async def download_image(url: str, file_name: str):
    folder = os.path.join(IMAGE_PATH, 'acggov')
    if not os.path.exists(folder):
        os.mkdir(folder)
    salt = ''.join(random.sample(string.ascii_letters + string.digits, 6))
    path = os.path.join(IMAGE_PATH, 'acggov', file_name)
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, proxy=PROXY) as resp:
                data = await resp.read()
                if USE_THUMB:
                    byte_stream = io.BytesIO(data)
                    roiImg = Image.open(byte_stream)
                    if roiImg.mode != 'RGB':
                        roiImg = roiImg.convert('RGB')
                    imgByteArr = io.BytesIO()
                    roiImg.save(imgByteArr, format='JPEG')
                    data = imgByteArr.getvalue()
                
                open(path, 'wb').write(data + bytes(salt, encoding="utf8"))
    except Exception as e:
        traceback.print_exc()
        return 1
    return 0

#获取随机色图
async def get_setu() -> (int, str):
    data = {}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get('https://api.acg-gov.com/public/setu') as resp:
                data = await resp.json(content_type='application/json')
    except Exception as e:
        traceback.print_exc()
        return 1, 'API访问异常'
    if 'data' not in data:
        return 1, '数据获取失败'
    data = data['data']
    illust = data['illust']
    title = data['title']
    author = data['user']['name']

    url = ''
    if USE_THUMB:
        url = data['large']
    else:
        num = random.randint(0, int(data['pageCount'])-1)
        url = data['originals'][num]['url']
    suffix = url.split('.')[-1]
    file_name = f'{illust}.{suffix}'
    if await download_image(url, file_name) == 0:
        return 0, f'[CQ:image,file=acggov/{file_name}]'
    else:
        return 1, '图片下载失败'

#获取排行榜
async def get_ranking(page: int = 0) -> (int, str):
    date = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    data = await query_ranking(date, page)
    if not 'response' in data:
        return 1, '数据获取失败'
    works = data['response'][0]['works']
    pages = data['pagination']['pages']
    current = data['pagination']['current']
    num = page * PER_PAGE + 1
    msg = ''
    for i in works:
        msg += f'{num}.' + i['work']['title'] + '-' + str(i['work']['id']) + '\n'
        num += 1
    msg += f'第{current}页，共{str(pages)}页'
    return 0, msg

#获取排行榜图片
async def get_ranking_setu(number: int) -> (int, str):
    page = number // PER_PAGE
    number = number % PER_PAGE

    date = (datetime.datetime.now() + datetime.timedelta(days=-2)).strftime("%Y-%m-%d")
    data = await query_ranking(date, page)
    if not 'response' in data:
        return 1, 'API访问异常'

    illust = data['response'][0]['works'][number]['work']['id']
    title = data['response'][0]['works'][number]['work']['title']
    author = data['response'][0]['works'][number]['work']['user']['name']
    url = ''
    if USE_THUMB:
        url = data['response'][0]['works'][number]['work']['image_urls']['large']
    else:
        data = {}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f'https://api.acg-gov.com/illusts/detail?illustId={illust}&reduction=true') as resp:
                    data = await resp.json(content_type='application/json')
        except Exception as e:
            traceback.print_exc()
            return 1, 'detail获取失败'
        if 'data' not in data:
            return 1, 'detail数据无效'
        data = data['data']
        page_count = data['illust']['page_count']
        if page_count == 1:
            url = data['illust']['meta_single_page']['original_image_url']
        else:
            meta_pages = data['illust']['meta_pages']
            num = random.randint(0, len(meta_pages)-1)
            url = meta_pages[num]['image_urls']['original']
    url = url.replace("https://i.pximg.net", "https://i.pixiv.cat")

    suffix = url.split('.')[-1]
    file_name = f'{illust}.{suffix}'
    if await download_image(url, file_name) == 0:
        return 0, f'id:{illust}\ntitle:{title}\nauthor:{author}\n[CQ:image,file=acggov/{file_name}]'
    else:
        return 1, '图片下载失败'
