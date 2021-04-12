#鉴于新版go-cqhttp支持临时私聊,对pjjc2作出部分修改
from json import load, dump
from nonebot import get_bot, on_command
from hoshino import priv, config
from hoshino.typing import NoticeSession, CommandSession
from .pcrclient import pcrclient, ApiException, bsdkclient
from asyncio import Lock
from os.path import dirname, join, exists
from copy import deepcopy
from traceback import format_exc
from .safeservice import SafeService
import time

sv_help = f'''
[竞技场绑定 uid] 绑定竞技场排名变动推送，默认双场均启用，仅排名降低时推送
[竞技场查询 (uid)] 查询竞技场简要信息，绑定后无需uid
[启用/停止(公主)竞技场订阅] 启用/停止(公主)竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
[详细查询 (uid)] 查询详细状态
[竞技场切换订阅 群聊/私聊] 私聊需要本群开启可发起临时会话
私聊需要Bot成为管理
'''.strip()


sv = SafeService('竞技场推送',help_=sv_help, bundle='查询')

async def self_member_info(bot, ev, gid):
    for sid in hoshino.get_self_ids():
        self_id = sid
        try:
            gm_info = await bot.get_group_member_info(
                group_id = gid,
                user_id = self_id,
                no_cache = True
            )
            return gm_info
        except Exception as e:
            hoshino.logger.exception(e)
            
    
@sv.on_fullmatch('帮助竞技场推送', only_to_me=False)
async def send_jjchelp(bot, ev):
    await bot.send(ev, sv_help)
        
curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'arena_bind' : {}
}

cache = {}
client = None
lck = Lock()

if exists(config):
    with open(config) as fp:
        root = load(fp)

binds = root['arena_bind']

captcha_lck = Lock()

with open(join(curpath, 'account.json')) as fp:
    acinfo = load(fp)

bot = get_bot()
validate = None
validating = False
acfirst = False

async def captchaVerifier(gt, challenge, userid):
    global acfirst, validating
    if not acfirst:
        await captcha_lck.acquire()
        acfirst = True
    
    if acinfo['admin'] == 0:
        bot.logger.error('captcha is required while admin qq is not set, so the login can\'t continue')
    else:
        url = f"https://help.tencentbot.top/geetest/?captcha_type=1&challenge={challenge}&gt={gt}&userid={userid}&gs=1"
        await bot.send_private_msg(
            user_id = acinfo['admin'],
            message = f'pcr账号登录需要验证码，请完成以下链接中的验证内容后将第一行validate=后面的内容复制，并用指令/pcrval xxxx将内容发送给机器人完成验证\n验证链接：{url}'
        )
    validating = True
    await captcha_lck.acquire()
    validating = False
    return validate

async def errlogger(msg):
    await bot.send_private_msg(
        user_id = acinfo['admin'],
        message = f'pcrjjc2登录错误：{msg}'
    )

bclient = bsdkclient(acinfo, captchaVerifier, errlogger)
client = pcrclient(bclient)

qlck = Lock()

async def query(id: str):
    if validating:
        raise ApiException('账号被风控，请联系管理员输入验证码并重新登录', -1)
    async with qlck:
        while client.shouldLogin:
            await client.login()
        res = (await client.callapi('/profile/get_profile', {
                'target_viewer_id': int(id)
            }))['user_info']
        return res

async def arena_query(id: str):
    if validating:
        raise ApiException('账号被风控，请联系管理员输入验证码并重新登录', -1)
    async with qlck:
        while client.shouldLogin:
            await client.login()
        res = (await client.callapi('/profile/get_profile', {
                'target_viewer_id': int(id)
            }))
        return res

def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)

@sv.on_rex(r'^竞技场绑定 ?(\d{13})$') #你可以修改第128行进行默认群聊与私聊的修改
async def on_arena_bind(bot, ev):
    global binds, lck

    async with lck:
        uid = str(ev['user_id'])
        last = binds[uid] if uid in binds else None

        binds[uid] = {
            'id': ev['match'].group(1),
            'uid': uid,
            'gid': str(ev['group_id']),
            'arena_on': last is None or last['arena_on'],
            'grand_arena_on': last is None or last['grand_arena_on'],
            'message':"group",
        }
        save_binds()

    await bot.finish(ev, '竞技场绑定成功', at_sender=True)

@sv.on_rex(r'^详细查询 ?(\d{13})?$')
async def on_query_arena_all(bot, ev):
    global binds, lck

    robj = ev['match']
    id = robj.group(1)

    async with lck:
        if id == None:
            uid = str(ev['user_id'])
            if not uid in binds:
                await bot.finish(ev, '您还未绑定竞技场', at_sender=True)
                return
            else:
                id = binds[uid]['id']
        try:
            res = await arena_query(id)
            arena_time = int (res['user_info']['arena_time'])
            arena_date = time.localtime(arena_time)
            arena_str = time.strftime('%Y-%m-%d',arena_date)

            grand_arena_time = int (res['user_info']['grand_arena_time'])
            grand_arena_date = time.localtime(grand_arena_time)
            grand_arena_str = time.strftime('%Y-%m-%d',grand_arena_date)
            
            await bot.finish(ev, 
f'''
id：{res['user_info']["viewer_id"]}
昵称：{res['user_info']["user_name"]}
公会：{res['clan_name']}
简介：{res['user_info']["user_comment"]}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
战力：{res['user_info']["total_power"]}
等级：{res['user_info']["team_level"]}
jjc场次：{res['user_info']["arena_group"]}
jjc创建日：{arena_str}
pjjc场次：{res['user_info']["grand_arena_group"]}
pjjc创建日：{grand_arena_str}
角色数：{res['user_info']["unit_num"]}/77
''', at_sender=True)
        except ApiException as e:
            await bot.finish(ev, f'查询出错，{e}', at_sender=True)

@sv.on_rex(r'^竞技场查询 ?(\d{13})?$')
async def on_query_arena(bot, ev):
    global binds, lck

    robj = ev['match']
    id = robj.group(1)

    async with lck:
        if id == None:
            uid = str(ev['user_id'])
            if not uid in binds:
                await bot.finish(ev, '您还未绑定竞技场', at_sender=True)
                return
            else:
                id = binds[uid]['id']
        try:
            res = await query(id)
            await bot.finish(ev, 
f'''
jjc：{res["arena_rank"]}
pjjc：{res["grand_arena_rank"]}''', at_sender=True)
        except ApiException as e:
            await bot.finish(ev, f'查询出错，{e}', at_sender=True)


@sv.on_rex('竞技场切换订阅 ?(群聊|私聊)')
async def change_arena_sub(bot, ev):
    global binds, lck
    
    uid = str(ev['user_id'])
    
    self_info = await self_member_info(bot, ev, gid)
    if self_info['role'] != 'owner' and self_info['role'] != 'admin':
        await bot.finish(ev, '\n我需要管理权限', at_sender=True)
        
    async with lck:
        if not uid in binds:
            await bot.send(ev,'您还未绑定竞技场',at_sender=True)
        else:
            if ev['match'].group(1) == '群聊':
                binds[uid]['message'] = 'group'
                save_binds()
                await bot.finish(ev, f'切换订阅至群聊成功', at_sender=True)
            elif ev['match'].group(1) == '私聊':
                binds[uid]['message'] = 'private'
                save_binds()
                await bot.finish(ev, f'切换订阅至私聊成功', at_sender=True)

@sv.on_rex('(启用|停止)(公主)?竞技场订阅')
async def change_arena_sub(bot, ev):
    global binds, lck

    key = 'arena_on' if ev['match'].group(2) is None else 'grand_arena_on'
    uid = str(ev['user_id'])

    async with lck:
        if not uid in binds:
            await bot.send(ev,'您还未绑定竞技场',at_sender=True)
        else:
            binds[uid][key] = ev['match'].group(1) == '启用'
            save_binds()
            await bot.finish(ev, f'{ev["match"].group(0)}成功', at_sender=True)

@on_command('/pcrval')
async def validate(session):
    global binds, lck, validate
    if session.ctx['user_id'] == acinfo['admin']:
        validate = session.ctx['message'].extract_plain_text().strip()[8:]
        captcha_lck.release()

@sv.on_prefix('删除竞技场订阅')
async def delete_arena_sub(bot,ev):
    global binds, lck

    uid = str(ev['user_id'])

    if ev.message[0].type == 'at':
        if not priv.check_priv(ev, priv.SUPERUSER):
            await bot.finish(ev, '删除他人订阅请联系维护', at_sender=True)
            return
        uid = str(ev.message[0].data['qq'])
    elif len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = str(ev['user_id'])


    if not uid in binds:
        await bot.finish(ev, '未绑定竞技场', at_sender=True)
        return

    async with lck:
        binds.pop(uid)
        save_binds()

    await bot.finish(ev, '删除竞技场订阅成功', at_sender=True)

@sv.on_fullmatch('竞技场订阅状态')
async def send_arena_sub_status(bot,ev):
    global binds, lck
    uid = str(ev['user_id'])

    
    if not uid in binds:
        await bot.send(ev,'您还未绑定竞技场', at_sender=True)
    else:
        info = binds[uid]
        await bot.finish(ev,
    f'''
    当前竞技场绑定ID：{info['id']}
    竞技场订阅：{'开启' if info['arena_on'] else '关闭'}
    公主竞技场订阅：{'开启' if info['grand_arena_on'] else '关闭'}''',at_sender=True)


@sv.scheduled_job('interval', minutes=.30) #轮询时间,自行根据负载修改
async def on_arena_schedule():
    global cache, binds, lck
    bot = get_bot()
    
    bind_cache = {}

    async with lck:
        bind_cache = deepcopy(binds)


    for user in bind_cache:
        info = bind_cache[user]
        try:
            sv.logger.info(f'querying {info["id"]} for {info["uid"]}')
            res = await query(info['id'])
            res = (res['arena_rank'], res['grand_arena_rank'])

            if user not in cache:
                cache[user] = res
                continue

            last = cache[user]
            cache[user] = res

            if res[0] > last[0] and info['arena_on']:
                if binds[info["uid"]]['message'] == 'private':
                    await bot.send_private_msg(
                        user_id = int(info["uid"]),
                        group_id = int(info['gid']),
                        message = f'jjc：{last[0]}->{res[0]} ▼{res[0]-last[0]}'
                    )
                else:
                    await bot.send_group_msg(
                        group_id = int(info['gid']),
                        message = f'[CQ:at,qq={info["uid"]}]jjc：{last[0]}->{res[0]} ▼{res[0]-last[0]}'
                    )
            if res[1] > last[1] and info['grand_arena_on']:
                if binds[info["uid"]]['message'] == 'private':
                    await bot.send_private_msg(
                        user_id = int(info["uid"]),
                        group_id = int(info['gid']),
                        message = f'pjjc：{last[1]}->{res[1]} ▼{res[1]-last[1]}'
                    )
                else:
                    await bot.send_group_msg(
                        group_id = int(info['gid']),
                        message = f'[CQ:at,qq={info["uid"]}]pjjc：{last[1]}->{res[1]} ▼{res[1]-last[1]}'
                    )
        except ApiException as e:
            sv.logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')
            if e.code == 6:

                async with lck:
                    binds.pop(user)
                    save_binds()
                sv.logger.info(f'已经自动删除错误的uid={info["id"]}')
        except:
            sv.logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')

@sv.on_notice('group_decrease.leave')
async def leave_notice(session: NoticeSession):
    global lck, bind
    uid = str(session.ctx['user_id'])
    
    async with lck:
        if uid in binds:
            binds.pop(uid)
            save_binds()
