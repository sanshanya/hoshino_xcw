from nonebot import MessageSegment
from hoshino import Service, priv, util, jewel
from hoshino.typing import CQEvent

sv_help = '''
-[查宝石]  查询拥有宝石
-[宝石群排行]  查看本群宝石数量最多的人
......更多功能有待开发
'''.strip()

sv = Service(
    name = '宝石银行',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

jewel_counter = jewel.jewelCounter()

@sv.on_fullmatch(["帮助宝石银行"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

@sv.on_prefix(['查宝石', '查询宝石', '查看宝石'])
async def get_jewel(bot, ev: CQEvent):
    gid = ev.group_id
    sid = None
    uid = ev.user_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    if uid == sid or priv.check_priv(ev,priv.ADMIN):
        try:
            current_jewel = jewel_counter._get_jewel(gid, uid)
            msg = f'您的宝石为{current_jewel}'
            await bot.send(ev, msg, at_sender=True)
            return
        except Exception as e:
            await bot.send(ev, '错误:\n' + str(e))

async def get_user_jewel_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card']!='' else m['nickname']
    return d

@sv.on_fullmatch(('宝石排行榜', '宝石群排行'))
async def description_guess_group_ranking(bot, ev: CQEvent):
    try:
        user_jewel_dict = await get_user_jewel_dict(bot, ev.group_id)
        jewel_num_dict = {}
        for uid in user_jewel_dict.keys():
            if uid != ev.self_id:
                jewel_num_dict[user_jewel_dict[uid]] = jewel_counter._get_jewel(ev.group_id, uid)
        group_ranking = sorted(jewel_num_dict.items(), key = lambda x:x[1], reverse = True)
        msg = '本群宝石排行榜:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i+1}名: {group_ranking[i][0]}, : {group_ranking[i][1]}颗\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))
        
@sv.on_prefix(('充值宝石'))
async def cheat_score(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦', at_sender=True)
    gid = ev.group_id
    uid = ev.user_id
    sid = None
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    jewel_counter._add_jewel(gid, sid, num)
    score = jewel_counter._get_jewel(gid, sid)
    msg = f'已为[CQ:at,qq={sid}]充值{num}宝石\n现在共有{score}宝石'
    await bot.send(ev, msg)
