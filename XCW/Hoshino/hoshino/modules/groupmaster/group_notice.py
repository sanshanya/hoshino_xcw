import hoshino
from hoshino import Service
from nonebot import *
import requests, os
bot=get_bot()
sv1 = Service('退群通知', help_='退群通知')


@sv1.on_notice('group_decrease')
async def leave_notice(session: NoticeSession):
    type = session.event['sub_type']
    uid = session.event['user_id']
    gid = session.event['group_id']
    pid = session.event['operator_id']
    at = MessageSegment.at(pid)
    data = await bot.get_stranger_info(user_id= uid)
    name = data['nickname']
    if type == 'kick':
        await session.send(f"{at}认为{name}({uid})不适合本群")
    elif type == 'leave':
        await session.send(f"{name}({uid})离开了我们，相信会有再见的一天！")


sv2 = Service('入群欢迎', help_='入群欢迎')



@sv2.on_notice('group_increase')
async def increace_welcome(session: NoticeSession):
    
    if session.event.user_id == session.event.self_id:
        return  # ignore myself
    gid = session.event['group_id']
    uid = session.event['user_id']
    await session.send(f'欢迎入群~', at_sender=True)