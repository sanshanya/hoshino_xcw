import os
import random
from hoshino.typing import CQEvent
from hoshino import R, Service
from nonebot import MessageSegment
from hoshino.modules.priconne import chara

sv = Service('pcr-record', help_='公主连结角色语音\n[语音+角色名]\n[角色名+语音] 听指定角色的语音\n例如: ue语音', visible=True, enable_on_default=True)

@sv.on_suffix('语音')
@sv.on_prefix('语音')
async def record_send(bot, ev: CQEvent):

    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"语音"+角色名，如"语音ue"')
        return
    cid = chara.name2id(name)
    if cid == chara.UNKNOWN:
        msg = f'兰德索尔似乎没有叫"{name}"的人...'
        await bot.send(ev, msg)
        return

    dir_path = R.get('record', str(cid)).path
    if not os.path.exists(dir_path):
        msg = f'未找到"{name}"的语音数据'
        await bot.send(ev, msg)
        return

    file_list = os.listdir(dir_path)
    file_path = None
    while not file_path or not os.path.isfile(file_path):
        filename = random.choice(file_list)
        file_path = os.path.join(dir_path, filename)
    if not file_path:
        msg = f'未找到"{name}"的语音数据'
        await bot.send(ev, msg)
        return
    rec = MessageSegment.record(f'file:///{os.path.abspath(file_path)}')
    await bot.send(ev, rec)