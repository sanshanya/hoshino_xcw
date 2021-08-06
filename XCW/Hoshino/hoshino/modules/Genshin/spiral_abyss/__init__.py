from requests.exceptions import ConnectionError, ReadTimeout
from hoshino import Service, priv, MessageSegment
from ..util import filter_list, get_next_day
from .query import abyss_use_probability, abyss_use_teams

sv_help = '''
[原神深渊速查] 查询一层深渊阵容推荐列表(不填参数默认12层)
[原神深渊使用率] 查询一层深渊角色使用率(不填参数默认12层)
'''.strip()

sv = Service(
    name='原神深渊速查',  # 功能名
    use_priv=priv.NORMAL,  # 使用权限
    manage_priv=priv.ADMIN,  # 管理权限
    visible=True,  # 可见性
    enable_on_default=True,  # 默认启用
    bundle = '原神', #分组归类
    help_=sv_help  # 帮助说明
)

prefix = '原神'


@sv.on_prefix((prefix + '深渊速查', prefix + '深境速查'))
async def main(bot, ev):
    keyword = ev.message.extract_plain_text().strip() or '12'
    try:
        img = await abyss_use_teams(floor=keyword)
        await bot.send(ev, MessageSegment.image(img), at_sender=True)
    except (ConnectionError, ReadTimeout) as e:
        await bot.send(ev, "请求数据失败,请稍后再试", at_sender=True)
        raise e


@sv.on_prefix((prefix + '深渊使用率', prefix + '深境使用率'))
async def main(bot, ev):
    keyword = ev.message.extract_plain_text().strip() or '12'
    try:
        img = await abyss_use_probability(floor=keyword)
        await bot.send(ev, MessageSegment.image(img), at_sender=True)
    except (ConnectionError, ReadTimeout) as e:
        await bot.send(ev, "请求数据失败,请稍后再试", at_sender=True)
        raise e
