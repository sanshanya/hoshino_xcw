from . import *


@on_command('变更所有授权',aliases=('批量变更','批量授权'), only_to_me=False)
async def add_time_all_chat(session):
    '''
    为所有已有授权的群增加授权x天, 可用于维护补偿时间等场景
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能批量授权哦')
        return
    if not session.current_arg:
        await session.finish('请发送需要为所有群增加或减少的长, 例如“变更所有授权 7”')
    
    days = int(session.current_arg.strip())

    authed_group_list = await util.get_authed_group_list()
    for ginfo in authed_group_list:
        util.change_authed_time(ginfo['gid'], days)
    
    await session.finish(f'已为所有群授权增加{days}天')

@on_command('授权列表', aliases=('查看授权列表', '查看全部授权', '查询全部授权'), only_to_me=True)
async def group_list_chat(session):
    '''
    此指令获得的是, 所有已经获得授权的群, 其中一些群可能Bot并没有加入 \n
    当授权群过多时,每页只显示5条
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能查看授权列表哦')
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

    authed_group_list = await util.get_authed_group_list()
    length = len(authed_group_list)

    groups_in_page = config.GROUPS_IN_PAGE
    pages_all = ceil(length/groups_in_page) # 向上取整
    if page > pages_all:
        await session.finish(f'没有那么多页, 当前共有授权信息{length}条, 共{pages_all}页')
    if page <= 0:
        await session.finish('请输入正确的页码')
    i = 0
    for item in authed_group_list:
        i = i + 1
        if i < (page-1)*groups_in_page+1 or i > page*groups_in_page:
            continue
        gid = int(item['gid'])
        g_time = util.check_group(gid)
        msg_new = await util.process_group_msg(gid,
                                               g_time,
                                               title=f'第{i}条信息\n',
                                               end='\n\n',
                                               group_name_sp=item['groupName'])
        msg += msg_new
        
    msg += f'第{page}页, 共{pages_all}页\n发送查询授权+页码以查询其他页'
    await session.send(msg)



@on_command('变更授权',aliases=('更改时间', '授权', '更改授权时间', '更新授权'),only_to_me=False)
async def add_time_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能变更授权哦')
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
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        session.finish('只有主人才能转移授权哦')
        return
    if not session.current_arg:
        await session.finish('请发送“转移授权 旧群群号*新群群号”来进行群授权转移')
    origin = session.current_arg.strip()
    pattern = re.compile(r'^(\d{5,15})\*(\d{5,15})$')
    m = pattern.match(origin)
    if m is None:
        await session.finish('格式错误或者群号错误XD\n请发送“转移授权 旧群群号*新群群号”来转移群授权时长\n如果新群已经授权，则会增加对应时长。')
    old_gid = int(m.group(1))
    new_gid = int(m.group(2))
    util.transfer_group(old_gid, new_gid)
    await session.send(f"授权转移成功~\n旧群【{old_gid}】授权已清空\n新群【{new_gid}】授权到期时间：{util.check_group(new_gid)}")


@on_command('授权状态', only_to_me=False)
async def auth_status_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能查看授权状态哦')
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
    agp_num = len(await util.get_authed_group_list())
    msg = f'Bot账号：{sid}\n所在群数：{gp_num}\n好友数：{fr_num}\n授权群数：{agp_num}\n未使用卡密数：{key_num}'
    await session.send(msg)


@on_command('清除授权',aliases=('删除授权','移除授权','移除群授权','删除群授权'),only_to_me=True)
async def remove_auth_chat(session):
    '''
    完全移除一个群的授权 \n
    不需要二次确认, 我寻思着你rm /* -rf的时候也没人让你二次确认啊  \n
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能清除授权哦')
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