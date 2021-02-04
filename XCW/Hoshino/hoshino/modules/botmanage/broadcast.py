import asyncio

import hoshino
from hoshino.service import sucmd
from hoshino.typing import CommandSession, CQHttpError


@sucmd('broadcast', aliases=('bc', '广播'))
async def broadcast(session: CommandSession):
    msg = session.current_arg
    for sid in hoshino.get_self_ids():
        gl = await session.bot.get_group_list(self_id=sid)
        gl = [ g['group_id'] for g in gl ]
        for g in gl:
            await asyncio.sleep(0.5)
            try:
                await session.bot.send_group_msg(self_id=sid, group_id=g, message=msg)
                hoshino.logger.info(f'群{g} 投递广播成功')
            except Exception as e:
                hoshino.logger.error(f'群{g} 投递广播失败：{type(e)}')
                try:
                    await session.send(f'群{g} 投递广播失败：{type(e)}')
                except Exception as e:
                    hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
    await session.send(f'广播完成！')

#私发机器人分群广播 [群号] [内容]
@sucmd('broadcastbygroup', aliases=('gbc', '分群广播','回话'))
async def broadcast(session: CommandSession):
    msg = session.current_arg.split(' ')
    try:
        target=int(msg[0])
    except Exception as e:
        hoshino.logger.error(f'投递分群广播失败：{type(e)}')
        try:
            await session.send(f'投递分群广播失败：{type(e)}')
        except Exception as e:
            hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
        return

    new_msg=' '.join(msg[1:])

    for sid in hoshino.get_self_ids():
        gl = await session.bot.get_group_list(self_id=sid)
        gl = [ g['group_id'] for g in gl ]
        if target not in gl:
            hoshino.logger.error('不在群中')
            try:
                await session.send('不在群中')
            except Exception as e:
                hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
            continue

        try:
            await session.bot.send_group_msg(self_id=sid, group_id=target, message=new_msg)
            hoshino.logger.info('分群投递广播成功')
        except Exception as e:
            hoshino.logger.error(f'分群投递广播失败：{type(e)}')
            try:
                await session.send(f'分群投递广播失败：{type(e)}')
            except Exception as e:
                hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')

    await session.send(f'广播完成！')