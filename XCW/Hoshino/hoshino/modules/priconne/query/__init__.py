from hoshino import Service, priv



sv_help = '''
- [pcr速查] 常用网址/图书馆
- [bcr速查] B服萌新攻略
- [挖矿15001] 矿场余钻
- [黄骑充电表] 黄骑1动规律
- [一个顶俩] 台服接龙小游戏
- [谁是霸瞳] 角色别称查询
'''.strip()

sv = Service(
    name = 'pcr常用查询',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '查询', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助pcr常用查询"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


from .whois import *
from .miner import *
