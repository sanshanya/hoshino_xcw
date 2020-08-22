from nonebot import on_command
from nonebot.exceptions import CQHttpError

from hoshino import R, Service, priv, util
from hoshino.typing import CQEvent
import re

RANKING_HELP = '''
[申请头衔] 自助授予群头衔(bot需具有群主权限)
'''.strip()

sv = Service('ranking', visible=True, manage_priv=priv.ADMIN, enable_on_default=True,help_=RANKING_HELP)

@sv.on_fullmatch(('ranking帮助', 'ranking幫助'))
async def ranking_help(bot, ev: CQEvent):
        await bot.send(ev, RANKING_HELP)


@sv.on_rex(r'(申请头衔|申請頭銜)(.*)')
async def ranking(bot, ev: CQEvent):

    qq_id = ev['user_id']

    groupid = ev['group_id']
    #rankname = str(ev['message']).strip().replace(' ','')
    match = ev['match']
    ranknamed = match.group(2)
    msg = f'设置头衔{ranknamed}成功'
    try:
            await bot.set_group_special_title(group_id=groupid,user_id=qq_id,special_title=ranknamed)
    except CQHttpError:
            pass
    await bot.send_group_msg(group_id=groupid,message=msg)