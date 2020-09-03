from . import *


@on_command('生成卡密', only_to_me=True)
async def creat_key_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        # 非超管, 忽略
        await session.finish('只有主人才能生成卡密哦')
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
        await session.finish('只有主人才能查看卡密列表哦')
        return
    if session.event.detail_type == 'group':
        # 群聊查看卡密你可真是个小天才
        await session.finish('憨批！私聊我查看剩余卡密啦！')
    if not session.current_arg.strip():
        # 无其他参数默认第一页
        page = 1  
    else:
        page = int(session.current_arg.strip())
    cards_in_page = config.CARDS_IN_PAGE
    key_list = util.get_key_list()
    length = len(key_list)
    pages_all = ceil(length/cards_in_page)

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
        if i < (page-1)*cards_in_page+1 or i > page*cards_in_page:
            continue
        msg += '卡密:' + items['key'] + '\n时长:' + str(items['duration']) + '天\n'
    msg += f'第{page}页, 共{pages_all}页\n发送卡密列表+页码以查询其他页'
    await session.send(msg)


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


@on_command('检验卡密',aliases=('检查卡密'), only_to_me=False)
async def check_card_chat(session):
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