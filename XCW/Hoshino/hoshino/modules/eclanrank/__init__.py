"""
作者艾琳有栖

版本 0.1.0

基于 nonebot pcr公会站排行插件

使用 会战排行关键字 查询一个公会名或者rank

会战锁定公会名 来进行锁定一个公会
会战解锁公会名 解锁一个公会

公会排行 查询绑定的公会


查询记录之前的排名

"""
from nonebot import *
from . import util
from . import clanrank
from . import locked
from hoshino import Service, priv  # 如果使用hoshino的分群管理取消注释这行

#
sv_help = '''
※最好不要和公会排名同时开启
- [会战锁定 公会名] 锁定一个公会
- [会战解锁 公会名] 解锁一个公会
- [公会排行] 查询锁定的公会
'''.strip()

sv = Service(
    name = '公会排名2',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '会战', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助公会排名2"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    



# 初始化配置文件
config = util.get_config()

# 初始化nonebot
_bot = get_bot()


@sv.on_message('group')  # 如果使用hoshino的分群管理取消注释这行 并注释下一行的 @_bot.on_message("group")
# @_bot.on_message("group") # nonebot使用这
async def epck_main(*params):
    bot, ctx = (_bot, params[0]) if len(params) == 1 else params

    msg = str(ctx['message']).strip()
    # 查询会战
    keyword = util.get_msg_keyword(config['comm']['keyword'], msg, True)
    if keyword:
        return await bot.send(ctx, clanrank.get_rank(keyword))
    # 会战锁定
    keyword = util.get_msg_keyword(config['comm']['locked'], msg, True)
    if keyword:
        return await bot.send(ctx, locked.lock(ctx, keyword))
    # 会战解锁
    keyword = util.get_msg_keyword(config['comm']['unlocked'], msg, True)
    if keyword:
        return await bot.send(ctx, locked.unlock(ctx, keyword))
    # 会战锁定查询
    keyword = util.get_msg_keyword(config['comm']['defaultLucked'], msg, True)
    if keyword == '':
        return await bot.send(ctx, locked.default_rank(ctx['group_id']))


