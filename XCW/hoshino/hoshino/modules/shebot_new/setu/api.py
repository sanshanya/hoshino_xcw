import asyncio
import aiohttp
import requests
import os
from io import BytesIO
from PIL import Image
from .config import APIKEY

class Setu:
    def __init__(self,pid,title,url,r18,tags,author):
        self.pid = pid
        self.title = title
        self.url = url
        self.r18 = r18
        self.tags = tags
        self.author = author

def get_setu(r18,keyword,num,size1200):
    apiPath=r'https://api.lolicon.app/setu'
    params = {'apikey':APIKEY,'r18':r18,'keyword':keyword,'num':num,'size1200':size1200}
    setu_list=[]
    try:
        with requests.get(apiPath,params=params,timeout=20) as resp:
            res = resp.json()
            data = res
            for item in data['data']:
                pid = item['pid']
                title = item['title']
                url = item['url']
                r18 = item['r18']
                tags = item['tags']
                author = item['author']
                setu = Setu(pid,title,url,r18,tags,author)
                setu_list.append(setu)
            return setu_list
    except Exception as ex:
        print(ex)
        print('多半是apikey填写错误或者ip被api屏蔽了，请尽快停止本插件')
    finally:
        return setu_list

async def Task (setu,storePath,PICTURES):
    url = setu.url
    r18 = setu.r18
    fileName = str(setu.pid)
    filePath = os.path.join(storePath,fileName)
    if os.path.exists(filePath):
        print('本地已有缓存')
        return
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print(f'当前url{url}')
            async with session.get(url) as resp:
                content = await resp.read()
                print('一张下载完成')
                with open(filePath,'wb') as f:
                    if r18==0:
                        f.write(content)
                        f.close()
                    elif r18==1:
                        img = Image.open(BytesIO(content))
                        img = img.convert('RGB')
                        img = img.transpose(Image.ROTATE_90)
                        out = BytesIO()
                        img.save(out,format='JPEG')
                        f.write(out.getvalue())
                        f.close()
                    PICTURES.append(setu)
    except Exception as ex:
        print(ex)

async def gather(setu_list,storePath,PICTURES):
    tasks = []
    for setu in setu_list:
        task = asyncio.create_task(Task(setu,storePath,PICTURES))
        tasks.append(task)
    await asyncio.gather(*tasks)

def get_final_setu(storePath,num=1,r18=2,keyword='',size1200='false'):
    PICTURES=[]
    setu_list = get_setu(r18=r18,num=num,keyword=keyword,size1200=size1200)
    asyncio.run(gather(setu_list,storePath,PICTURES))
    return PICTURES
    
async def get_final_setu_async(storePath,num=1,r18=2,keyword='',size1200='false'):
    setu_list = get_setu(r18=r18,num=num,keyword=keyword,size1200=size1200)
    return setu_list



