import re
import json
import requests
import datetime

from hoshino import Service
from hoshino.typing import CQEvent, MessageSegment

sv = Service('traceanime', help_='''
[搜番+图片] 根据图片查询番剧
'''.strip())

@sv.on_prefix(('搜番', '查番'))
async def traceanime(bot, ev: CQEvent):
    ret = re.match(r"\[CQ:image,file=(.*),url=(.*)\]", str(ev.message))
    pic_url = ret.group(2)
    url = f'https://trace.moe/api/search?url={pic_url}'
    try:
        with requests.get(url, timeout=20) as resp:
            res = resp.json()
            data = res['docs'][0]
            print(data)
            similarity = "%.2f%%" % (data['similarity'] * 100)
            episode = data['episode']
            time = datetime.timedelta(seconds=data['at'])
            title_native = data['title_native']
            title_chinese = data['title_chinese']
            title_english = data['title_english']
            limit = res['limit']
            limit_ttl = res['limit_ttl']
            is_adult = '分级：普通'
            if data['is_adult']:
                is_adult = '分级：限制级'
            if data['similarity'] < 0.70:
                msg = '没有查询到结果，可能原因：图片为局部图/图片清晰度太低。。。'
            else:
                if type(episode) is int:
                    msg = f'[{similarity}]该截图出自第{episode}集{time}\n{title_native}\n{title_chinese}\n{title_english}\n{is_adult}'
                else:
                    msg = f'[{similarity}]该截图出自{episode}{time}\n{title_native}\n{title_chinese}\n{title_english}\n{is_adult}'
            await bot.send(ev, msg+'\n剩余查询次数:'+str(limit)+'，查询数+1剩余时间:'+str(limit_ttl)+'s')
    except Exception as ex:
        print(ex)
        await bot.send(ev, '查询错误，请稍后重试。。。')

#后续计划，交互友好度，额外返回番剧信息
#如果搜索图像为空，API 将返回 HTTP 400
#如果使用无效令牌，API 将返回 HTTP 403
#如果使用请求太快，API 将返回 HTTP 429
#如果后端出现问题，API 将返回 HTTP 500 或 HTTP 503
