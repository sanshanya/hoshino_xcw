#Created by ColdThunder11 2021/1/3
#changed by lulu to another api 2021/1/7
from os import path
import json
from hoshino import Service, priv
import nonebot
from hoshino.typing import NoticeSession
import asyncio
from .queryapi import getprofile
import copy

sv_help = '''
- [竞技场绑定 uid] 绑定竞技场排名变动推送（仅下降），默认双场均启用
- [竞技场查询( uid)] 查询竞技场简要信息
- [停止竞技场订阅] 停止战斗竞技场排名变动推送
- [停止公主竞技场订阅] 停止公主竞技场排名变动推送
- [启用竞技场订阅] 启用战斗竞技场排名变动推送
- [启用公主竞技场订阅] 启用公主竞技场排名变动推送
- [删除竞技场订阅 (@sb)] 删除竞技场排名变动推送绑定,默认自己，可以@sb
- [竞技场订阅状态] 查看排名变动推送绑定状态
'''.strip()

sv = Service(
    name = '竞技场推送',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '查询', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助竞技场推送"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

Inited = False
pcrprofile = None
binds = {}
arena_ranks = {}
grand_arena_ranks ={}
tr = None

@sv.on_fullmatch('jjc帮助', only_to_me=False)
async def send_jjchelp(bot, ev):
    await bot.send(ev, sv_help)

def Init():
    global Inited
    global pcrprofile
    global binds
    global tr
    Inited = True
    config_path = path.join(path.dirname(__file__),"binds.json")
    with open(config_path,"r",encoding="utf8")as fp:
        binds = json.load(fp)

def save_binds():
    config_path = path.join(path.dirname(__file__),"binds.json")
    jsonStr = json.dumps(binds, indent=4)
    with open(config_path,"r+",encoding="utf8")as fp:
        fp.truncate(0)
        fp.seek(0)
        fp.write(jsonStr)

@sv.on_rex(r'竞技场绑定 (.{0,15})$')
async def on_arena_bind(bot,ev):
    global binds
    if not Inited:
        Init()
    robj = ev['match']
    id = robj.group(1)
    if not id.isdigit() or not len(id) == 13:
        await bot.send(ev,"ID格式错误，请检查",at_sender=True)
        return
    uid = str(ev['user_id'])
    gid = str(ev['group_id'])
    if not uid in binds["arena_bind"]:
        binds["arena_bind"][uid] = {"id":id,"uid":uid,"gid":gid,"arena_on":True,"grand_arena_on":True}
    else:
        binds["arena_bind"][uid]["id"] = id
        binds["arena_bind"][uid]["uid"] = uid
        binds["arena_bind"][uid]["gid"] = gid
    save_binds()
    await bot.send(ev,"竞技场绑定成功",at_sender=True)

@sv.on_rex(r'(竞技场查询 (.{0,15})$)|(^竞技场查询$)')
async def on_query_arena(bot,ev):
    if not Inited:
        Init()
    robj = ev['match']
    try:
        id = robj.group(2)
    except:
        id = ""
    if id=='' or id==None:
        uid = str(ev['user_id'])
        if not uid in binds["arena_bind"]:
            await bot.send(ev,"您还未绑定竞技场",at_sender=True)
            return
        else:
            id = binds["arena_bind"][uid]["id"]
    if not id.isdigit() or not len(id) == 13:
        await bot.send(ev,"ID格式错误，请检查",at_sender=True)
        return
    try:
        res = await getprofile(int(id))
        res = res["user_info"]
        '''if res["err_code"] == 403:
            sv.logger.info("您的API KEY错误或者被屏蔽，请尽快停止本插件")
            await bot.send(ev,"错误403，查询出错，请联系维护者",at_sender=True)
            return'''
        if res == "queue":
            sv.logger.info("成功添加至队列"),
            await bot.send(ev,"请等待源站更新数据，稍等几分钟再来查询",at_sender=True)
        if res == "id err":
            sv.logger.info("该viewer_id有误")
            await bot.send(ev,"查询出错，请检查ID是否正确",at_sender=True)
            return
        strList = []
        strList.append("\n")
        strList.append("竞技场排名：")
        strList.append(str(res["arena_rank"]))
        strList.append("\n")
        strList.append("公主竞技场排名：")
        strList.append(str(res["grand_arena_rank"]))
        await bot.send(ev,"".join(strList),at_sender=True)
    except:
        await bot.send(ev,"查询出错，请检查ID是否正确",at_sender=True)
    pass

@sv.on_fullmatch('停止竞技场订阅')
async def disable_arena_sub(bot,ev):
    if not Inited:
        Init()
    uid = str(ev['user_id'])
    if not uid in binds["arena_bind"]:
        await bot.send(ev,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["arena_on"] = False
        save_binds()
        await bot.send(ev,"停止竞技场订阅成功",at_sender=True)

@sv.on_fullmatch('停止公主竞技场订阅')
async def disable_grand_arena_sub(bot,ev):
    if not Inited:
        Init()
    uid = str(ev['user_id'])
    if not uid in binds["arena_bind"]:
        await bot.send(ev,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["grand_arena_on"] = False
        save_binds()
        await bot.send(ev,"停止公主竞技场订阅成功",at_sender=True)

@sv.on_fullmatch('启用竞技场订阅')
async def enable_arena_sub(bot,ev):
    if not Inited:
        Init()
    uid = str(ev['user_id'])
    if not uid in binds["arena_bind"]:
        await bot.send(ev,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["arena_on"] = True
        save_binds()
        await bot.send(ev,"启用竞技场订阅成功",at_sender=True)

@sv.on_fullmatch('启用公主竞技场订阅')
async def enable_arena_sub(bot,ev):
    if not Inited:
        Init()
    uid = str(ev['user_id'])
    if not uid in binds["arena_bind"]:
        await bot.send(ev,"您还未绑定竞技场",at_sender=True)
    else:
        binds["arena_bind"][uid]["grand_arena_on"] = True
        save_binds()
        await bot.send(ev,"启用公主竞技场订阅成功",at_sender=True)

@sv.on_prefix('删除竞技场订阅')
async def delete_arena_sub(bot,ev):
    if not Inited:
        Init()
    if len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = str(ev['user_id'])
        if not uid in binds["arena_bind"]:
            await bot.finish(ev, "您还未绑定竞技场", at_sender=True)
        else:
            binds["arena_bind"].pop(uid)
            save_binds()
            await bot.send(ev, "删除竞技场订阅成功", at_sender=True)
    elif ev.message[0].type == 'at':
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '删除他人订阅请联系维护', at_sender=True)
        else:
            uid = str(ev.message[0].data['qq'])
            if not uid in binds["arena_bind"]:
                await bot.finish(ev, "对方尚未绑定竞技场", at_sender=True)
            else:
                binds["arena_bind"].pop(uid)
                save_binds()
                await bot.send(ev, "删除竞技场订阅成功", at_sender=True)
    else:
        await bot.finish(ev, '参数格式错误, 请重试')

@sv.on_fullmatch('竞技场订阅状态')
async def send_arena_sub_status(bot,ev):
    if not Inited:
        Init()
    uid = str(ev['user_id'])
    if not uid in binds["arena_bind"]:
        await bot.send(ev,"您还未绑定竞技场",at_sender=True)
    else:
        strList = []
        strList.append("当前竞技场绑定ID：")
        strList.append(str(binds["arena_bind"][uid]["id"]))
        strList.append("\n竞技场订阅：")
        if binds["arena_bind"][uid]["arena_on"]:
            strList.append("开启")
        else:
            strList.append("关闭")
        strList.append("\n公主竞技场订阅：")
        if binds["arena_bind"][uid]["grand_arena_on"]:
            strList.append("开启")
        else:
            strList.append("关闭")
        await bot.send(ev,"".join(strList),at_sender=True)

@sv.scheduled_job('interval', minutes=1)
async def on_arena_schedule():
    global arena_ranks
    global grand_arena_ranks
    bot = nonebot.get_bot()
    if not Inited:
        Init()
    arena_bind = copy.deepcopy(binds["arena_bind"])
    for user in arena_bind:
        user = str(user)
        await asyncio.sleep(1.5)
        try:
            res = await getprofile(int(binds["arena_bind"][user]["id"]))
            res = res["user_info"]
            if binds["arena_bind"][user]["arena_on"]:
                if not user in arena_ranks:
                    arena_ranks[user] = res["arena_rank"]
                else:
                    origin_rank = arena_ranks[user]
                    new_rank = res["arena_rank"]
                    if origin_rank >= new_rank:#不动或者上升
                        arena_ranks[user] = new_rank
                    else:
                        msg = "[CQ:at,qq={uid}]您的竞技场排名发生变化：{origin_rank}->{new_rank}".format(uid=binds["arena_bind"][user]["uid"], origin_rank=str(origin_rank), new_rank=str(new_rank))
                        arena_ranks[user] = new_rank
                        await bot.send_group_msg(group_id=int(binds["arena_bind"][user]["gid"]),message=msg)
            if binds["arena_bind"][user]["grand_arena_on"]:
                if not user in grand_arena_ranks:
                    grand_arena_ranks[user] = res["grand_arena_rank"]
                else:
                    origin_rank = grand_arena_ranks[user]
                    new_rank = res["grand_arena_rank"]
                    if origin_rank >= new_rank:#不动或者上升
                        grand_arena_ranks[user] = new_rank
                    else:
                        msg = "[CQ:at,qq={uid}]您的公主竞技场排名发生变化：{origin_rank}->{new_rank}".format(uid=binds["arena_bind"][user]["uid"], origin_rank=str(origin_rank), new_rank=str(new_rank))
                        grand_arena_ranks[user] = new_rank
                        await bot.send_group_msg(group_id=int(binds["arena_bind"][user]["gid"]),message=msg)
        except:
            sv.logger.info("对{id}的检查出错".format(id=binds["arena_bind"][user]["id"]))

@sv.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    if not Inited:
        Init()
    uid = str(session.ctx['user_id'])
    if not uid in binds["arena_bind"]:
        pass
    else:
        binds["arena_bind"].pop(uid)
        save_binds()
        pass
    return
