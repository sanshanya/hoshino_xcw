import random
import hoshino
from hoshino import Service, aiorequests, priv

sv_help = '''
无
'''.strip()

sv = Service(
    name = 'deepchat',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = False, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助deepchat"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)


@sv.on_message('group')
async def deepchat(bot, ctx):
    msg = ctx['message'].extract_plain_text()
    if not msg or random.random() > 0.025:
        return
    payload = {
        "msg": msg,
        "group": ctx['group_id'],
        "qq": ctx['user_id']
    }
    sv.logger.debug(payload)
    api = hoshino.config.deepchat.deepchat_api
    rsp = await aiorequests.post(api, data=payload, timeout=10)
    rsp = await rsp.json()
    sv.logger.debug(rsp)
    if rsp['msg']:
        await bot.send(ctx, rsp['msg'])
