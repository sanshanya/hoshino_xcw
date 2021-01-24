from nonebot import *
from hoshino import R, Service, priv, util

bot=get_bot()

sv_help = '''
- 防止撤回desi~
'''.strip()

sv = Service(
    name = '防撤回',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助防撤回"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

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