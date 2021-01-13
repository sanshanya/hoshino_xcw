from nonebot import on_command, CommandSession
from hoshino import R, Service, priv, util, config

sv = Service('回响', visible= False, enable_on_default= True, bundle='回响', help_='''
- 念念不忘 必有回响
'''.strip())

def CQ_trans(cqcode:str) -> str:
    CQcode = cqcode
    CQcode = CQcode.replace('&#44;',',')
    CQcode = CQcode.replace('&amp;','&')
    CQcode = CQcode.replace('&#91;','[')
    CQcode = CQcode.replace('&#93;',']')
    return CQcode

def CQ_detrans(cqcode:str) -> str:
    CQcode = cqcode
    CQcode = CQcode.replace('&','&amp;')
    CQcode = CQcode.replace('[','&#91;')
    CQcode = CQcode.replace(']','&#93;')
    return CQcode

@sv.on_command('echo', aliases=('回响'), only_to_me=False)
async def echo(session: CommandSession):
    CQcode = session.get('CQcode', prompt="你想回响什么呢?")
    res = CQ_trans(CQcode)
    if res:
        await session.send(res)
    else:
        await session.send("[ERROR]Not found translate_Info")

@sv.on_command('echo2', aliases=('回响2'), only_to_me=False)
async def echo2(session: CommandSession):
    CQcode = session.get('CQcode', prompt="你想回响什么呢?")
    res = CQ_trans(CQcode)
    res = CQ_trans(res)
    if res:
        await session.send(res)
    else:
        await session.send("[ERROR]Not found translate_Info")

@sv.on_command('parse', aliases=('解析'), only_to_me=False)
async def parse(session: CommandSession):
    CQcode = session.get('CQcode', prompt="你想解析什么呢?")
    res = CQ_detrans(CQcode)
    if res:
        await session.send(res)
    else:
        await session.send("[ERROR]Not found translate_Info")
        
@echo.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['CQcode'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要回响的内容称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg

@parse.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['CQcode'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要解析的内容称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg

@echo2.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['CQcode'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要回响的内容称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg
