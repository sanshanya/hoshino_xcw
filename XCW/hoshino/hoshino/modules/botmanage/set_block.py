import hoshino
import re
from datetime import timedelta
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv_help = '''
- [拉黑x分钟@成员] 拉黑指定群员x分钟
- [拉黑x小时@成员] 拉黑指定群员x小时
- [拉黑x天@成员] 拉黑指定群员x天
'''.strip()

sv = Service(
    name = '拉黑',  #功能名
    use_priv = priv.ADMIN, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助拉黑"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    
    

@sv.on_prefix('拉黑')
async def set_block(bot, ev: CQEvent):
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