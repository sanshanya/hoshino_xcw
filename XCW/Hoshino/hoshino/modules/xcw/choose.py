import random
from hoshino import Service,priv

sv_help = '''
遇事不决问问xcw吧~
- [要X还是Y] xcw帮你抉择哦~
'''.strip()

sv = Service(
    name = '遇事不决',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助遇事不决"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_prefix(('要'))
async def hp_choose(bot, ev):
    message = ev.message.extract_plain_text().strip()
    msg = message[0:].split('还是')
    if len(msg) == 1:
        return
    choices=list(filter(lambda x:len(x)!=0,msg))
    if not choices:
        await bot.send(ev,'选项不能全为空！',at_sender=True)
        return 
    msgs=['建议您选择: ']
    if random.randrange(1000)<=100:
        msgs.append('“我全都要”')
    else:
        final=random.choice(choices)
        msgs.append(f'{final}')
        await bot.send(ev,'\n'.join(msgs),at_sender=True)