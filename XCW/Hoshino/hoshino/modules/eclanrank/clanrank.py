from typing import List
import time
import asyncio
import math
import nonebot
from nonebot import *
from nonebot.log import logger
from . import query
from . import util

# 初始化配置文件
config = util.get_config()
line_db = util.init_db(config.cache_dir, 'line.sqlite')


def get_rank(keyword):
    # 首先不管怎么样先转换到字符串
    keyword = f'{keyword}'.strip()

    # 这家伙怎么不传东西近来
    if not keyword:
        return '要写公会名啦!'

    # 判断是否由全数字组成 是就转换成数字  否则就是原来的参数
    keyword = math.floor(int(keyword)) if keyword.isdigit() else keyword

    params = {}

    if isinstance(keyword, int):
        params['rank'] = keyword
    else:
        params['name'] = keyword

    info, ts = query.get_rank(**params)

    if not info:
        return '木有找到相关的工会'

    return print_rank(info, ts=ts)


def print_rank(info, new_info=None, ts=None):
    res = query.get_line()
    res.reverse()
    line_db['line'] = res

    if not info:
        return ''
    info: List[query.get_rank_response] = info if isinstance(info, list) else [info]
    if new_info:
        new_info: List[query.get_rank_response] = new_info if isinstance(new_info, list) else [new_info]
    message: List[MessageSegment] = []
    text = MessageSegment.text
    for index, data in enumerate(info):
        rank_ext = ''
        damage_ext = ''
        if new_info:
            new = new_info[index]
            rank_calc = new.rank - data.rank
            damage_calc = new.damage - data.damage
            rank_ext = f'▼{rank_calc}' if rank_calc > 0 else f'▲{abs(rank_calc)}'
            damage_ext = f'▲{format(damage_calc, ",")}'
            data = new
        data.data['ts'] = ts if ts else time.strftime(config.str.ts_formet, time.localtime())
        data.data['rank_ext'] = rank_ext
        data.data['score'] = format(data.damage, ",")
        data.data['score_ext'] = damage_ext
        data.data['process'] = util.calc_hp(data.damage)
        message.append(*Message(config.str.print_rank_info.format(**data.data)))
        line = line_db.get('line', [])
        if line:
            target = util.filter_list(line, lambda x: x['damage'] > data.damage)
            if not target:
                info, ts = query.get_rank(rank=1)
                target = [info[0].data]
            target = target[0]
            message.append(
                text(f'档线 -> 排行[ {target["rank"]} ] 相差[ {format(target["damage"] - data.damage, ",")} ]分数\n'))
        message.append(text(f'——————————————\n'))
    return message[:-1]


async def update_line():
    res = query.get_line()
    if not res:
        logger.error('档线更新失败。 请检查相关设置')
        return
    res.reverse()
    line_db['line'] = res
    logger.info('定时任务：更新会战档线成功')


def run_init():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(update_line())
    loop.close()


run_init()
