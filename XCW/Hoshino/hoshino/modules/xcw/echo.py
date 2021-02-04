from nonebot import on_command, CommandSession
from hoshino import R, Service, priv, util, config

sv_help = '''
- [echo XX] xx可以是图片/文字/CQ码
- [parse XX] xx可以是图片/文字/CQ码
※回响与解析能够相互配合
- [CQ码帮助] 获取CQ码的简易帮助
'''.strip()

sv_help1 = '''
CQ码的简易帮助建议配合解析
- CQ:image,file=图片名.image,url=XXX 图片类
- CQ:tts,text=这是一条测试消息 文字转语音
- CQ:cardimage,file=XX 卡片类
注意CQ码外部应该是[]框住
......
'''.strip()


sv = Service(
    name = '回响及解析',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助回响"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    
@sv.on_fullmatch(["CQ码帮助"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help1, at_sender=True)

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


