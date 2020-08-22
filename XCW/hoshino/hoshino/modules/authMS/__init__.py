'''
贡献名单：
wdvxdr1123,火龙|PurinBot,var-mixer
'''
from datetime import *
import re, asyncio
import nonebot
from nonebot import on_command, on_request
import hoshino
from hoshino import msghandler, priv, Service
from .web_server import auth
from . import util
from math import ceil
# 取消以下两行注释以web服务,注意web下部分功能可能于本插件不兼容
 app = nonebot.get_bot().server_app
 app.register_blueprint(auth)  

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict
trial_list = msghandler.trial_list

try:
    config = hoshino.config.authMS.auth_config
except:
    # 保不准哪个憨憨又不读README呢
    hoshino.logger.error('authMS无配置文件!请仔细阅读README')


@on_command('生成卡密', only_to_me=True)
async def creat_key_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        # 非超管, 忽略
        return
    if session.event.detail_type == 'group':
        # 群聊生成卡密你可真是个小天才
        await session.finish('请私聊机器人生成')
        return
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{1,5})\*(\d{1,3})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('格式输错了啦憨批！请按照“生成卡密 时长*数量”进行输入！')
    duration = int(m.group(1))
    key_num = int(m.group(2))
    if key_num <= 0 or duration <= 0:
        await session.finish('你搁那生你🐴空气呢？')
    key_list = []
    for _ in range(key_num):
        new_key = util.add_key(duration)
        hoshino.logger.info(f'已生成新卡密{new_key}, 有效期{duration}天')
        key_list.append(new_key)
    await session.send(f'已生成{key_num}份{duration}天的卡密：\n' + '\n'.join(key_list))


@on_command('卡密列表', only_to_me=True)
async def key_list_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    if session.event.detail_type == 'group':
        # 群聊生成卡密你可真是个小天才
        await session.finish('请机器人维护者私聊机器人查看剩余卡密')

    if not session.current_arg.strip():
        # 无其他参数默认第一页
        page = 1  
    else:
        page = int(session.current_arg.strip())

    key_list = util.get_key_list()
    length = len(key_list)
    pages_all = ceil(length/10)

    if page > pages_all:
        await session.finish(f'没有那么多页, 当前共有卡密共{length}条, 共{pages_all}页')
    if page <= 0:
        await session.finish('请输入正确的页码')

    if not length:
        await session.finish('无可用卡密信息')
    
    msg = '======卡密列表======\n'
    i = 0
    for items in key_list:
        i = i + 1
        if i < (page-1)*10+1 or i > (page-1)*10+10:
            continue
        msg += '卡密:' + items['key'] + '\n时长:' + str(items['duration']) + '天\n'
    msg += f'第{page}页, 共{pages_all}页\n发送卡密列表+页码以查询其他页'
    await session.send(msg)


@on_command('授权列表', aliases=('查看授权列表', '查看全部授权', '查询全部授权'), only_to_me=False)
async def group_list_chat(session):
    '''
    此指令获得的是, 所有已经获得授权的群, 其中一些群可能Bot并没有加入 \n
    当授权群过多时,每页只显示5条
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    if session.event.detail_type == 'group':
        # 群聊查看授权列表你也是个小天才
        await session.finish('请超级管理员私聊机器人查看授权列表')

    if not session.current_arg.strip():
        # 无其他参数默认第一页
        page = 1  
    else:
        page = int(session.current_arg.strip())

    msg = '======授权列表======\n'

    authed_group_list = util.get_authed_group_list()
    length = len(authed_group_list)
    pages_all = ceil(length/5) # 向上取整
    if page > pages_all:
        await session.finish(f'没有那么多页, 当前共有授权信息{length}条, 共{pages_all}页')
    if page <= 0:
        await session.finish('请输入正确的页码')
    i = 0
    for item in authed_group_list:
        i = i + 1
        if i < (page-1)*5+1 or i > (page-1)*5+5:
            continue
        gid = int(item['gid'])
        g_time = util.check_group(gid)
        msg_new = await util.process_group_msg(gid,
                                               g_time,
                                               title=f'第{i}条信息\n',
                                               end='\n\n')
        msg += msg_new
        
    msg += f'第{page}页, 共{pages_all}页\n发送查询授权+页码以查询其他页'
    await session.send(msg)


@on_command('查询授权', only_to_me=False)
async def auth_query_chat(session):
    if session.event.detail_type == 'private':
        # 私聊同样处理比较复杂, 且需判断是否是数字
        if not session.current_arg:
            await session.finish('私聊查询请发送“查询授权 群号”来进行指定群的授权查询（请注意空格）')
        gid = session.current_arg.strip()
        if not gid.isdigit():
            await session.finish('请输入正确的群号')

    elif session.event.detail_type == 'group':
        gid = session.event.group_id

    result = util.check_group(gid)
    if not result:
        msg = '此群未获得授权'
    else:
        msg = await util.process_group_msg(gid, result, title='授权查询结果\n')
    await session.finish(msg)


@on_command('充值', only_to_me=False)
async def reg_group_chat(session):
    if not session.current_arg:
        # 检查参数
        await session.finish(
            '私聊充值请发送“充值 卡密*群号”\n群聊充值请发送“充值 卡密”\n部分机器人可能不允许私聊充值，请留意空格')

    if session.event.detail_type == 'private':
        # 私聊充值
        if not config.ALLOW_PRIVATE_REG:
            await session.finish('本机器人已关闭私聊充值，请直接在群聊中发送“充值 卡密”来为本群充值')

        origin = session.current_arg.strip()
        pattern = re.compile(r'^(\w{16})\*(\d{5,15})$')
        m = pattern.match(origin)
        if m is None:
            # 检查格式
            msg = '充值格式错误...\n私聊使用卡密请发送“充值 卡密*群号”, 例如 充值 GTa2Nw0unPU95xqO*123456789'
            await session.finish(msg)
        key = m.group(1)
        gid = m.group(2)

    elif session.event.detail_type == 'group':
        # 群聊情况比较简单
        gid = session.event.group_id
        key = session.current_arg.strip()
    else:
        # 讨论组搁这儿充值你🐎呢
        return

    result = util.reg_group(gid, key)

    if result == False:
        # 充值失败
        msg = '卡密无效, 请检查是否有误或已被使用, 如果无此类问题请联系发卡方'
    else:
        msg = await util.process_group_msg(gid, result, '充值成功\n')
    await session.finish(msg)


@on_command('变更授权',aliases=('更改时间', '授权', '更改授权时间', '更新授权'),only_to_me=False)
async def add_time_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})([+-]\d{1,5})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('请发送“授权 群号±时长”来进行指定群的授权, 时长最长为99999')
    gid = int(m.group(1))
    days = int(m.group(2))
    result = util.change_authed_time(gid, days)
    msg = await util.process_group_msg(gid, result, title='变更成功, 变更后的群授权信息:\n')
    await session.finish(msg)


@on_command('转移授权', only_to_me=False)
async def group_change_chat(session):

    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        session.finish('仅超级管理员可转移授权')

    if not session.current_arg:
        await session.finish('请发送“转移授权 旧群群号*新群群号”来进行群授权转移')
    today = datetime.now()
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})\*(\d{5,15})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish(
            '格式错误或者群号错误XD\n请发送“转移授权 旧群群号*新群群号”来转移群授权时长\n如果新群已经授权, 则会增加对应时长。')
    o_gid = int(m.group(1))
    o_gid = int(m.group(2))
    if o_gid in group_dict:
        left_time = group_dict[o_gid] - today
        group_dict[o_gid] = group_dict[o_gid] + left_time
        group_dict.pop(o_gid)
        await session.send(
            f"授权转移成功~\n旧群【{o_gid}】授权已清空\n新群【{o_gid}】授权到期时间：{group_dict[o_gid].isoformat()}"
        )
    else:
        group_dict[o_gid] = group_dict[o_gid]
        group_dict.pop(o_gid)
        await session.send(
            f"授权转移成功~\n旧群【{o_gid}】授权已清空\n新群【{o_gid}】授权到期时间：{group_dict[o_gid].isoformat()}"
        )


@on_command('授权状态', only_to_me=False)
async def auth_status_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    for sid in hoshino.get_self_ids():
        sgl = set(g['group_id']
                  for g in await session.bot.get_group_list(self_id=sid))
        frl = set(f['user_id']
                  for f in await session.bot.get_friend_list(self_id=sid))
    # 直接从service里抄了, 面向cv编程才是真
    gp_num = len(sgl)
    fr_num = len(frl)
    key_num = len(util.get_key_list())
    agp_num = len(util.get_authed_group_list())
    msg = f'Bot账号：{sid}\n所在群数：{gp_num}\n好友数：{fr_num}\n授权群数：{agp_num}\n未使用卡密数：{key_num}'
    await session.send(msg)


@on_command('清除授权',aliases=('删除授权','移除授权','移除群授权','删除群授权'),only_to_me=True)
async def remove_auth_chat(session):
    '''
    完全移除一个群的授权 \n
    不需要二次确认, 我寻思着你rm /* -rf的时候也没人让你二次确认啊  \n
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    if not session.current_arg.strip():
        await session.finish('请输入正确的群号, 例如“清除授权 123456789”')
    gid = int(session.current_arg.strip())
    time_left = util.check_group(gid)
    if not time_left:
        await session.finish('此群未获得授权')
    msg = await util.process_group_msg(gid=gid,expiration=time_left,title='已移除授权,原授权信息如下\n')
    util.change_authed_time(gid=gid, operate='clear')

    if config.AUTO_LEAVE:
        try:
            await session.bot.send_group_msg(group_id=gid,message=config.GROUP_LEAVE_MSG)
            await session.bot.set_group_leave(group_id=gid)
            msg += '\n已退出该群聊'
        except Exception as e:
            hoshino.logger.error(f'退出群{gid}时发生错误{type(e)}')
    await session.send(msg)

@on_command('退群', only_to_me=False)
async def group_leave_chat(session):
    '''
    退群, 并不影响授权, 清除授权请试用清除授权命令
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    try:
        gid = int(session.current_arg.strip())
        await session.send('正在褪裙...')
        await session.bot.send_group_msg(group_id=gid,message=config.GROUP_LEAVE_MSG)
        await session.bot.set_group_leave(group_id=gid)
    except Exception as e:
        await session.send('退群失败')
        hoshino.logger.error(f'退出群聊{gid}时失败, 发生错误{type(e)}')


@on_command('检验卡密',only_to_me=False)
async def view_aut_list(session):
    if session.event.detail_type == 'private' and not config.ALLOW_PRIVETE_CHECK:
        await session.finish('管理员已禁止私聊检查卡密, 请在群内使用')
    if not session.current_arg:
        await session.finish('检验卡密请发送“检验卡密 卡密”哦~')
    else:
        origin = session.current_arg.strip()
        pattern = re.compile(r'^(\w{16})$')
        m = pattern.match(origin)
        if m is None:
            await session.finish('格式输错了啦憨批！请按照“检验卡密 卡密”进行输入！')
        key = m.group(1)
        if duration := util.query_key(key):
            await session.finish(f'该卡密有效!\n授权时长:{duration}天')
        else:
            await session.finish(f'该卡密无效!')

