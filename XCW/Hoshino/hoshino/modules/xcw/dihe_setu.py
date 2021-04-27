import requests
from hoshino import Service,priv
from nonebot import MessageSegment
from nonebot.exceptions import CQHttpError
sv_help = f'''
地河可爱
'''.strip()

sv = Service(
    name = 'dihe_setu',
    use_priv = priv.NORMAL,
    manage_priv = priv.ADMIN,
    visible = True,
    enable_on_default = True,
    bundle = '通用',
    help_ = sv_help
    )


@sv.on_fullmatch(["地河可爱"])
async def setu(bot, ev):
    r = requests.get('https://api.dihe.moe/setu/?r18=0')
    j = r.json()
    try:
        rec = MessageSegment.image(j['url'])
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_fullmatch(["地河超可爱"])
async def setu1(bot, ev):
    r = requests.get('https://api.dihe.moe/setu/?r18=1')
    j = r.json()
    try:
        rec = MessageSegment.image(j['url'])
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")


