from hoshino import Service,priv


sv_help = '''
禁止套娃
'''.strip()

sv = Service(
    name = 'taowa',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助套娃"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_suffix('套娃')
async def nodolls(bot, ev):
    msg = ev.message.extract_plain_text().strip().strip(":").strip("。")
    reply = f'禁止{msg}套娃'
    await bot.send(ev, reply)
