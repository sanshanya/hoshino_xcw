import hoshino
import re
from datetime import timedelta
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('拉黑', visible= False, enable_on_default= True, bundle='拉黑', help_='''
- [拉黑x分钟@成员] 拉黑指定群员x分钟
- [拉黑x小时@成员] 拉黑指定群员x小时
- [拉黑x天@成员] 拉黑指定群员x天
'''.strip())

@sv.on_prefix('拉黑')
async def set_block(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS:
        return
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            kw = '12小时'
            time = { '小时': 12, '分钟': 0, '天': 0 }
            for msg in ev.message:
                if msg.type == 'text':
                    kw = msg.data['text'].replace(' ', '')
                    t_match = re.search(r'(?P<num>[0-9]+)(?P<tp>小时|天|分|分钟)', kw)
                    if t_match and int(t_match.group('num')) > 0:
                        time = { '小时': 0, '分钟': 0, '天': 0 }
                        t = t_match.group('tp')
                        t = t if t != '分' else '分钟'
                        time[t] = int(t_match.group('num'))
                    break
            uid = int(m.data['qq'])
            hoshino.priv.set_block_user(uid,timedelta(days=time['天'],minutes=time['分钟'],hours=time['小时']))
            await bot.send(ev, f"已拉黑{kw}")
            return