from nonebot import *
from hoshino import R, Service, priv, util

bot=get_bot()
sv = Service('防撤回', visible= False, enable_on_default= False, bundle='防撤回', help_='''
- 防止撤回desi~
'''.strip())
def CQ_trans(cqcode:str) -> str:
    CQcode = cqcode
    CQcode = CQcode.replace('&#44;',',')
    CQcode = CQcode.replace('&amp;','&')
    CQcode = CQcode.replace('&#91;','[')
    CQcode = CQcode.replace('&#93;',']')
    return CQcode
    
@sv.on_notice('group_recall')
async def new_longwang(session: NoticeSession):
    uid = session.event['user_id']
    gid = session.event['group_id']
    pid = session.event['operator_id']
    mid = session.event['message_id']
    msgs = await bot.get_msg(message_id=mid)
    CQcode = msgs['message']
    msg = CQ_trans(CQcode)
    at = MessageSegment.at(pid)
    name = msgs['sender']['nickname']
    msg = f'{at}撤回了{name}的消息\n>{msg}'
    await session.send(msg)