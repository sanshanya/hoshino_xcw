import requests
import os
import json
import re
import random

from hoshino.service import Service

config_path = os.path.dirname(__file__)+'/config.json'
sv = Service('longwang',enable_on_default=True)

@sv.on_keyword(keywords=('迫害龙王'))
async def _(bot,ctx):
    gid = ctx.get('group_id')
    try:
        cookies = await bot.get_cookies(domain='qun.qq.com')
    except:
        await bot.send(ctx,'获取cookies失败')
    headers = {
        "cookie" : cookies['cookies']
    }
    url = f'https://qun.qq.com/interactive/honorlist?gc={gid}&type=1'
    with requests.post(url,headers=headers) as resp:
        text = resp.text
        json_text = re.search('window.__INITIAL_STATE__=(.+?)</script>',text).group(1)
        data = json.loads(json_text)
        dragon_king = data['talkativeList'][0]['uin']
    replys = [
        '龙王出来喷水',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154128.jpg]',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154141.jpg]',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154148.jpg]',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154153.jpg]',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154205.jpg]',
        '[CQ:image,file=EPK自定义回复\QQ图片20200621154322.jpg]'
        
    ]
    reply = random.sample(replys,1)[0]
    await bot.send(ctx,f'[CQ:at,qq={dragon_king}] {reply}')