import re
import math
import random



from hoshino import Service, priv, util
from hoshino.typing import CQEvent

sv_help = '''
- [精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
- [给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
'''.strip()

sv = Service(
    name = '睡眠套餐',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助睡眠套餐"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


@sv.on_fullmatch(('睡眠套餐', '休眠套餐', '精致睡眠', '来一份精致睡眠套餐', '精緻睡眠', '來一份精緻睡眠套餐'))
async def sleep_8h(bot, ev):
    await util.silence(ev, 8*60*60, skip_su=False)


@sv.on_rex(r'(来|來)(.*(份|个)(.*)(睡|茶)(.*))套餐')
async def sleep(bot, ev: CQEvent):
    base = 0 if '午' in ev.plain_text else 5*60*60
    length = len(ev.plain_text)
    sleep_time = base + round(math.sqrt(length) * 60 * 30 + 60 * random.randint(-15, 15))
    await util.silence(ev, sleep_time, skip_su=False)
