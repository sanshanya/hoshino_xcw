import pytz
import random
from datetime import datetime
from hoshino import util
from hoshino import R
from hoshino.service import Service, priv

sv_help = '''
国服的买药提醒的说
'''.strip()

sv = Service(
    name = '买药提醒',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '订阅', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助买药提醒"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

def get_hour_call():
    """从HOUR_CALLS中挑出一组时报，每日更换，一日之内保持相同"""
    config = util.load_config(__file__)
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    hc_groups = config["HOUR_CALLS"]
    g = hc_groups[ now.day % len(hc_groups) ]
    return config[g]

@sv.scheduled_job('cron', hour='*', )
async def hour_call():
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    if not now.hour % 6 == 0:
        return
    await sv.broadcast(str(R.img(f"yao{random.randint(1, 5)}.png").cqcode), 'hourcall', 0)