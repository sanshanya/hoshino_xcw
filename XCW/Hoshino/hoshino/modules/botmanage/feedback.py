import hoshino
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv_help = '''
- [来杯咖啡] 后接反馈内容 联系维护组 请不要反馈无意义的事情
'''.strip()

sv = Service(
    name = '来杯咖啡',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助来杯咖啡"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    




@sv.on_prefix('来杯咖啡')
async def feedback(bot, ev: CQEvent):
    uid = ev.user_id
    coffee = hoshino.config.SUPERUSERS[0]
    text = str(ev.message).strip()
    if not text:
        await bot.send(ev, f"请发送来杯咖啡+您要反馈的内容~", at_sender=True)
    else:
        await bot.send_private_msg(self_id=ev.self_id, user_id=coffee, message=f'@群{ev.group_id}\nQQ:{uid}\n{text}')
        await bot.send(ev, f'您的反馈已发送至维护组！\n======\n{text}', at_sender=True)

