import os
import random


from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment


from hoshino import R, Service, priv


sv = Service('xcw语音', visible= True, enable_on_default= True, bundle='xcw语音', help_='''
- [@bot 骂我] xcw就会真的骂你
'''.strip())
xcw_folder = R.get('record/xcw/').path


def get_xcw():
    files = os.listdir(xcw_folder)
    filename = random.choice(files)
    rec = R.get('record/xcw/', filename)
    return rec


@sv.on_fullmatch('骂我', only_to_me=True)
async def xcw(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_xcw()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")
