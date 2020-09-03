from . import *

@on_request('friend')
async def friend_approve(session):
    if config.FRIEND_APPROVE:
        hoshino.logger.info(f'已自动接收来自{session.event.user_id}的好友请求')
        await session.approve()
    else:
        hoshino.logger.info(f'收到来自{session.event.user_id}的好友请求')
    
    