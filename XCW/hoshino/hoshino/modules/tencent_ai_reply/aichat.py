from nonebot import MessageSegment
import os
import asyncio
import time
import json
import traceback
import nonebot
import random
import threading 
import re
import string
from hashlib import md5
from time import time
from urllib.parse import quote_plus

import aiohttp
from nonebot import get_bot
from nonebot.helpers import render_expression
from hoshino import Service, priv
#from hoshino.service import Service, Privilege as Priv
sv = Service('人工智障', enable_on_default=False)

try:
    import ujson as json
except ImportError:
    import json

bot = get_bot()
cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
salt = None

# 定义无法获取回复时的「表达（Expression）」
EXPR_DONT_UNDERSTAND = (
    '我现在还不太明白你在说什么呢，但没关系，以后的我会变得更强呢！',
    '我有点看不懂你的意思呀，可以跟我聊些简单的话题嘛',
    '其实我不太明白你的意思……',
    '抱歉哦，我现在的能力还不能够明白你在说什么，但我会加油的～',
    '唔……等会再告诉你'
)

################
# 请修改
app_id = '2154605859'
app_key = 'DWmXnuZXkI9rnvKN'
################

def getReqSign(params: dict) -> str:
    hashed_str = ''
    for key in sorted(params):
        hashed_str += key + '=' + quote_plus(params[key]) + '&'
    hashed_str += 'app_key='+app_key
    sign = md5(hashed_str.encode())
    return sign.hexdigest().upper()


def rand_string(n=8):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n))

path = os.path.join(os.path.dirname(__file__),'ai_config.json')
def save_config(config:dict):
    try:
        with open(path,'w',encoding='utf8') as f:
            json.dump(config,f,ensure_ascii=False,indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False

def load_config():
    try:
        with open(path,'r',encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}
config_path = os.path.dirname(__file__)+'/config.json'
g_config = load_config()
g_open_groups = set(g_config.get('open_groups',[]))

@sv.on_message()
async def switch(bot, ctx):
    global g_config
    global g_open_groups
    msg = ctx['raw_message']
    switch.gpid = ctx['group_id']
    u_priv = priv.get_user_priv(ctx)
    if u_priv < priv.ADMIN:
        return
    if msg == '提高AI概率':
        g_open_groups.add(switch.gpid)
        g_config['open_groups'] = list(g_open_groups)
        save_config(g_config)
        await bot.send(ctx,'本群AI概率已提高',at_sender=True)

    elif msg == '降低AI概率':
        g_open_groups.discard(switch.gpid)
        g_config['open_groups'] = list(g_open_groups)
        save_config
        await bot.send(ctx,'本群AI概率已降低',at_sender=True)
        
@sv.on_message('group')
async def ai_reply(bot, context):
    if switch.gpid not in g_open_groups and switch.gpid!= 0:
            if not random.randint(1,100) <= 0.5:#拙劣的概率开关
                return

    msg = str(context['message'])
    if msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        return

    text = re.sub(cq_code_pattern, '', msg).strip()
    if text == '':
        return

    global salt
    if salt is None:
        salt = rand_string()
    session_id = md5((str(context['user_id'])+salt).encode()).hexdigest()

    param = {
        'app_id': app_id,
        'session': session_id,
        'question': text,
        'time_stamp': str(int(time())),
        'nonce_str': rand_string(),
    }
    sign = getReqSign(param)
    param['sign'] = sign

    async with aiohttp.request(
        'POST',
        'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat',
        params=param,
    ) as response:
        code = response.status
        if code != 200:
            raise ValueError(f'bad server http code: {code}')
        res = await response.read()
        #print (res)
    param = json.loads(res)
    if param['ret'] != 0:
        raise ValueError(param['msg'])
    reply = param['data']['answer']
    if reply:
        await bot.send(context, reply,at_sender=False) 
    else:
        # 如果调用失败，或者它返回的内容我们目前处理不了，发送无法获取回复时的「表达」
        # 这里的 render_expression() 函数会将一个「表达」渲染成一个字符串消息
        await bot.send(render_expression(EXPR_DONT_UNDERSTAND))