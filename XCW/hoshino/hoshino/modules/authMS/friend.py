from nonebot import on_request

import hoshino

from .constant import config
from . import util



@on_request('friend')
async def friend_approve(session):
    if config.FRIEND_APPROVE:
        util.log(f'已自动接受来自{session.event.user_id}的好友请求','friend_add')
        hoshino.logger.info(f'已自动接受来自{session.event.user_id}的好友请求')
        await session.approve()
    else:
        util.log(f'收到来自{session.event.user_id}的好友请求','friend_add')
        hoshino.logger.info(f'收到来自{session.event.user_id}的好友请求')
