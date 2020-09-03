from typing import Any, Callable, Dict
from aiocqhttp.message import MessageSegment
import nonebot
from aiocqhttp.event import Event
from nonebot.message import Message
import re

class VarHandler:
    def  __init__(self) -> None:
        self.allvar = {}

    def add(self, var: str, func: Callable) -> None:
        self.allvar[var] = func

    def find_func(self, var: str) -> Callable:
        return self.allvar.get(var)

var_handler = VarHandler()
def replace(origin_msg_str: str, event: Event) -> MessageSegment:
    allvar = re.findall('【.+?】', origin_msg_str) #取出变量列表,变量可能含有参数

    if not allvar:
        #没有变量，直接返回原消息 
        return origin_msg_str

    replaced_msg_str = origin_msg_str

    for compelete_v in allvar:
        # 取出参数列表
        args = [x.strip('<').strip('>') for x in re.findall('<.+?>', compelete_v)]
        stripped_v = re.sub('<.+?>', '', compelete_v)
        func = var_handler.find_func(stripped_v)
        if func:
            try:
                replace_msg = func(*args) 
            except TypeError: #异常说明函数需要event参数
                replace_msg = func(*args, event)
            except:
                replace_msg = compelete_v
                continue
            replaced_msg_str = replaced_msg_str.replace(compelete_v, str(replace_msg))
        else:
            continue #没有找到处理函数
    return replaced_msg_str

def add_replace(var_name: str):
    def deco(func):
        var = f'【{var_name}】'
        var_handler.add(var, func)
    return deco

bot = nonebot.get_bot()
@bot.before_sending
async def var_replace(event: Event, message: Message, kwargs: Dict[str, Any]):
    origin_msg_str = str(message)
    repaced_msg_str = replace(origin_msg_str, event)
    message.clear()
    message.extend(repaced_msg_str)



from hoshino.util4sh import get_random_file, Res as R
from os import path
"""
可以按照如下格式添加变量，如果需要使用event，添加在最后一个参数
返回值为str或者MessageSegment
"""
@add_replace('随机图片')
def random_pic(folder: str) -> 'MessageSegment':
    #例 【随机图片<智乃>】
    pic = get_random_file(path.join(R.image_dir, folder))
    return R.image(f'{folder}/{pic}')

@add_replace('艾特全体')
def at_all() -> 'MessageSegment':
    return MessageSegment.at('all')

@add_replace('艾特当前')
def at_current(event: Event) -> 'MessageSegment':
    return MessageSegment.at(event.user_id)
