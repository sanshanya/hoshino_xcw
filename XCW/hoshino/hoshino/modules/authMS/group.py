from . import *
tz =  pytz.timezone('Asia/Shanghai')
from datetime import *


@on_request('group')
async def approve_group_invite(session):
    '''
    自动处理入群邀请  \n
    由于腾讯憨批, 现在被邀请加入50人以下的群不需要验证, 因此此条目只适用于50人以上的邀请的情况, 50人以下请参见下一条函数\n
    请注意, 应当移除其他@on_request('group.add')或者其他入群管理,以防止冲突, 例如移除botmanager下的join_approve \n

    拒绝入群条件: \n
    1. 新群且试用期设置为0 \n
    2. 群授权已过期(新群试用也视为有授权, 期间内可自由加入)

    v0.1.1后新增, 配置ENABLE_AUTH为假的时候, 不检查授权
    '''

    if not config.ENABLE_AUTH:
        # 配置ENABLE_AUTH为0, 则授权系统不起作用, 不会自动通过加群邀请
        return

    if session.event.sub_type != 'invite':
        return
    gid = session.event.group_id
    ev = session.event
    
    new_group_auth = util.new_group_check(gid)
    if new_group_auth == 'expired' or new_group_auth == 'no trial':
        await session.bot.set_group_add_request(flag=ev.flag,
                                                    sub_type=ev.sub_type,
                                                    approve=False,
                                                    reason='此群授权已到期, 续费请联系维护组')
        hoshino.logger.info(f'接受到加群邀请,群号{gid}授权状态{new_group_auth}, 拒绝加入')
    elif new_group_auth == 'authed' or new_group_auth == 'trial':
        await session.bot.set_group_add_request(flag=ev.flag,
                                                sub_type=ev.sub_type,
                                                approve=True)
        hoshino.logger.info(f'接受到加群邀请,群号{gid}授权状态{new_group_auth}, 同意加入')
    else:
        pass


@on_notice('group_increase')
async def approve_group_invite_auto(session):
    '''
    被邀请加入50人以下群时会自动接受, 此时获得的事件类型为通知而非邀请 \n
    无法处理拒绝入群的邀请, 应当使用退群(如果开启了自动退群的话)
    '''
    self_ids = session.bot._wsr_api_clients.keys()
    for item in self_ids:
        sid = item
    gid = session.event.group_id
    if int(session.event.user_id) != int(sid):
        # 入群的人不是自己
        return
    
    new_group_auth = util.new_group_check(gid)
    if new_group_auth == 'expired' or new_group_auth == 'no trial':
        if config.AUTO_LEAVE:
            await session.bot.set_group_leave(group_id=gid)
            hoshino.logger.info(f'被强制拉入群{gid}中,该群授权状态{new_group_auth}, 已自动退出')
    elif new_group_auth == 'authed' or new_group_auth == 'trial':
        await asyncio.sleep(1) # 别发太快了
        msg = config.NEW_GROUP_MSG
        try:
            # 考虑全体禁言的情况, 使用try
            await session.bot.send_group_msg(group_id=gid,message= msg)
        except Exception as e:
            hoshino.logger.error(f'向新群{gid}发送消息失败, 发生错误{type(e)}')
            pass
    hoshino.logger.info(f'被强制拉入群{gid}中,该群授权状态{new_group_auth}')


@on_command('退群', only_to_me=False)
async def group_leave_chat(session):
    '''
    退群, 并不影响授权, 清除授权请试用清除授权命令
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能让我退群哦')
        return
    gid = int(session.current_arg.strip())
    await session.send('正在褪裙...')
    try:
        await session.bot.send_group_msg(group_id=gid,message=config.GROUP_LEAVE_MSG)
    except Exception as e:
        await session.send(f'发送退群发言时发生错误{type(e)}, 可能被禁言')
    try:
        await session.bot.set_group_leave(group_id=gid)
        await session.send(f'已成功退出群{gid}')
    except Exception as e:
        await session.send(f'退群失败, 发生错误{type(e)}')


@on_command('快速检查',only_to_me=True)
async def quick_check_chat(session):
    '''
    立即执行一次检查, 内容与定时任务一样
    '''
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    await check_auth()
    await session.finish('检查完成')

async def check_auth():
    '''
    检查所有已加入群的授权
    '''
    bot = nonebot.get_bot()
    group_info_all = await util.get_group_list_all()
    for group in group_info_all:
        gid = group['group_id']
        if gid in group_dict:
            hoshino.logger.info(f'正在检查群{gid}的授权......')
            # 此群已有授权或曾有授权, 检查是否过期
            time_left = group_dict[gid] - datetime.now()
            days_left = time_left.days

            if time_left.total_seconds() <= 0:
                # 已过期
                msg_expired = await util.process_group_msg(
                    gid=gid,
                    expiration=group_dict[gid],
                    title='【提醒】本群授权已过期\n',
                    end='如果需要续费请联系机器人维护',
                    group_name_sp=group['group_name'])
                try:
                    # 使用try以防止机器人被禁言或者被迅速踢出等情况
                    await bot.send_group_msg(group_id=gid,
                                                     message=msg_expired)
                except Exception as e:
                    hoshino.logger.error(f'向群{gid}发送过期提醒时发生错误{type(e)}')

                if config.AUTO_LEAVE:
                    try:
                        # 使用try以防止机器人被迅速踢出而导致群不存在等情况
                        await bot.set_group_leave(group_id=gid)
                    except Exception as e:
                        hoshino.logger.error(f'群{gid}授权过期,但退群时发生错误{type(e)}')
                    hoshino.logger.info(f'群{gid}授权过期,已自动退群')
                group_dict.pop(gid)

            if days_left < config.REMIND_BRFORE_EXPIRED and days_left >= 0:
                # 将要过期
                msg_remind = await util.process_group_msg(
                    gid=gid,
                    expiration=group_dict[gid],
                    title=f'【提醒】本群的授权已不足{days_left+1}天\n',
                    end='\n如果需要续费请联系机器人维护',
                    group_name_sp=group['group_name'])
                try:
                    await bot.send_group_msg(group_id=gid,
                                                     message=msg_remind)
                except Exception as e:
                    hoshino.logger.error(f'向群{gid}发生到期提醒消息时发生错误{type(e)}')
            hoshino.logger.info(f'群{gid}的授权不足{days_left+1}天')
        
        elif gid not in trial_list:
            # 正常情况下, 无论是50人以上群还是50人以下群, 都需要经过机器人同意或检查
            # 但是！如果机器人掉线期间被拉进群试用, 将无法处理试用, 因此有了这部分憨批代码

            if not config.NEW_GROUP_DAYS and config.AUTO_LEAVE:
                # 无新群试用机制,直接退群
                await bot.send_group_msg(group_id=gid,message=config.GROUP_LEAVE_MSG)
                hoshino.logger.info(f'发现无记录而被自动拉入的新群{gid}, 已退出此群')
                await bot.set_group_leave(group_id=gid)
                continue
            else:
                util.new_group_check(gid)
                hoshino.logger.info(f'发现无记录而被自动拉入的新群{gid}, 已开始试用')