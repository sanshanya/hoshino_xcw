import time
from itertools import groupby
import nonebot
import asyncio
from nonebot import *
from nonebot.log import logger
from . import query
from . import clanrank
from . import util

bot = get_bot()
config = util.get_config()
db = util.init_db(config.cache_dir)

admins = config.admins
admins = set((admins if isinstance(admins, list) else [admins]) + bot.config.SUPERUSERS)


def __check_params__(ctx, target):
    failed = True
    target = f'{target}'.strip()
    if not target:
        return failed, '阿勒？!'
    is_super_admin = ctx['user_id'] in admins
    is_admin = util.is_group_admin(ctx) or is_super_admin

    if config.rules.only_admin_can_locked and not is_admin:
        return failed, '只有管理员才可以锁定公会', '', 0

    target = target.split("#")
    try:
        name, uid = (target[0], 0) if len(target) == 1 else (target[0], int(target[1]))
    except Exception as e:
        logger.info(e)
        return failed, '参数错啦', '', 0

    return False, '', name, uid


def lock(ctx, target):
    failed, msg, name, uid = __check_params__(ctx, target)
    if failed:
        return msg

    info, ts = query.get_rank(name=name)
    if not info:
        return '锁定失败 木有找到相关工会'

    if len(info) > 1 and not uid:
        msg = clanrank.print_rank(info, ts=ts)
        msg.append(MessageSegment.text(f'\n找到多个公会请详细指定公会名，如重复使用[ 会战锁定{name}#UID ]来锁定'))
        return msg

    return __save_lock__(info, ctx['group_id'], uid)


def __save_lock__(info, group_id, uid=0, update=False):
    info = info if isinstance(info, list) else [info]
    if not info or not group_id:
        return '锁定失败~'

    if uid:
        info = util.filter_list(info, lambda x: x.leader_viewer_id == uid)
        if not info:
            return '锁定失败！找不到指定uid的公会'
    data: query.get_rank_response = info[0]
    group = db.get(group_id, [])

    if bool(util.filter_list(group, lambda x: x['leader_viewer_id'] == data.leader_viewer_id)):
        return '你已经锁定过公会了 不能再锁定啦'

    if config.rules.only_one_locked and bool(len(group)):
        return '锁定失败！不能锁定更多公会啦'

    data.group_id = group_id
    group.append(data.data)
    db[group_id] = group

    return '锁定成功~ 可以直接使用会战查询本公会，不需要带名字'


def unlock(ctx, target):
    failed, msg, name, uid = __check_params__(ctx, target)
    if failed:
        return msg
    group_id = ctx['group_id']
    group = db.get(group_id, [])

    # 仅判断是否有多个相同名字的公会在列表里  实际上还是group来做处理
    info = util.filter_list(group, lambda x: x['clan_name'] == name)

    if len(info) > 1 and not uid:
        msg = clanrank.print_rank(info)
        msg.append(MessageSegment.text(f'\n解锁失败 [ 会战锁定{name}#UID ]来解除'))
        return msg

    is_del_flag = False
    del_index = 0
    for index, value in enumerate(group):
        if value['clan_name'] == name:
            if uid and value['leader_viewer_id'] == uid:
                del_index = index
                is_del_flag = True
                break
            del_index = index
            is_del_flag = True

    if is_del_flag:
        group.pop(del_index)
        if bool(group):
            db[group_id] = group
        else:
            db.pop(group_id)
        return '解锁成功~'
    else:
        return '唔 解锁失败了 请根据 会战锁定{name}#UID 来解除'


def __failed_get_info__(info):
    return f'检查不到这公会的数据了 可到 https://kengxxiao.github.io/Kyouka/ 查询 也或者 会战解锁{info["clan_name"]}#{info["leader_viewer_id"]}'


def default_rank(group_id):
    group = db.get(group_id, [])
    if not group:
        return '还没有绑定公会呢 快用 会战锁定公会名 来进行绑定'
    res = []
    for value in group:
        info, ts = query.get_rank(name=value['clan_name'], uid=value['leader_viewer_id'])
        if not info:
            return __failed_get_info__(value)
        res.append(*info)

    return clanrank.print_rank(res, ts=ts)


async def check_rank_state():
    # # 更新一下现在的档线
    # await clanrank.update_line()

    group_list = groupby(sum(db.values(), []), lambda x: x['clan_name'])
    for key, group in group_list:
        logger.info(f'正在更新：{key} 公会')
        info, ts = query.get_rank(name=key)
        for data in group:
            group_id = data['group_id']
            # 如果这公会不存在了就广播吧
            if not info:
                await bot.send_group_msg(group_id=group_id, message=__failed_get_info__(data))
                continue
            # 做个检验 防止是多个公会
            new_info: query.get_rank_response = \
                util.filter_list(info, lambda x: x.leader_viewer_id == data['leader_viewer_id'])[0]
            try:
                await bot.send_group_msg(group_id=group_id,
                                         message=clanrank.print_rank(query.get_rank_response(data), new_info, ts=ts))
            except Exception as e:
                if e == 103:
                    logger.info(f'群：{group_id} 不存在')
                    continue
                logger.error(e)
                continue
            # 完事后更新数据库
            db_list = db.get(group_id, [])
            for index, value in enumerate(db_list):
                if value['clan_name'] == new_info.clan_name and value['leader_viewer_id'] == new_info.leader_viewer_id:
                    new_info.group_id = group_id
                    db_list[index] = new_info.data
                    break
            db[group_id] = db_list
        await asyncio.sleep(1)


if config.rules.enable_clan_cron:
    @nonebot.scheduler.scheduled_job(
        'cron',
        hour=f"*/{config.rules.lock_clan_cron_time}"
    )
    async def _():
        await check_rank_state()

if config.rules.enable_broadcast_time:
    @nonebot.scheduler.scheduled_job(
        'cron',
        **config.rules.broadcast_time
    )
    async def _():
        await check_rank_state()
