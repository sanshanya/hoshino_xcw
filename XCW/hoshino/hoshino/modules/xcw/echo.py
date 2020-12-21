from nonebot import on_command
from hoshino import R, Service, priv, util, config

sv = Service('回响', visible= False, enable_on_default= True, bundle='回响', help_='''
- 念念不忘 必有回响
'''.strip())

def CQ_trans(cqcode:str) -> str:
    CQcode = cqcode
    CQcode = CQcode.replace('&amp;','&')
    CQcode = CQcode.replace('&#91;','[')
    CQcode = CQcode.replace('&#93;',']')
    return CQcode

@on_command('echo', only_to_me=False)
async def echo(session):
    CQcode = session.current_arg.strip()
    if session.event.user_id not in config.SUPERUSERS or not CQcode:
        return
    else:
        CQcode = CQ_trans(CQcode)
        await session.finish(CQcode)
        
