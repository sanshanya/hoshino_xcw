import random

import hoshino
from hoshino import Service, priv, util
from hoshino.typing import CQEvent, CQHttpError, Message

sv_help = '''
基本对话
'''.strip()

sv = Service(
    name = '随机复读',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助随机复读"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

PROB_A = 1.4
group_stat = {}     # group_id: (last_msg, is_repeated, p)

'''
不复读率 随 复读次数 指数级衰减
从第2条复读，即第3条重复消息开始有几率触发复读

a 设为一个略大于1的小数，最好不要超过2，建议1.6
复读概率计算式：p_n = 1 - 1/a^n
递推式：p_n+1 = 1 - (1 - p_n) / a
'''
@sv.on_message()
async def random_repeater(bot, ev: CQEvent):
    group_id = ev.group_id
    msg = str(ev.message)

    if group_id not in group_stat:
        group_stat[group_id] = (msg, False, 0)
        return

    last_msg, is_repeated, p = group_stat[group_id]
    if last_msg == msg:     # 群友正在复读
        if not is_repeated:     # 机器人尚未复读过，开始测试复读
            if random.random() < p:    # 概率测试通过，复读并设flag
                try:
                    group_stat[group_id] = (msg, True, 0)
                    await bot.send(ev, util.filt_message(ev.message))
                except CQHttpError as e:
                    hoshino.logger.error(f'复读失败: {type(e)}')
                    hoshino.logger.exception(e)
            else:                      # 概率测试失败，蓄力
                p = 1 - (1 - p) / PROB_A
                group_stat[group_id] = (msg, False, p)
    else:   # 不是复读，重置
        group_stat[group_id] = (msg, False, 0)


def _test_a(a):
    '''
    该函数打印prob_n用于选取调节a
    注意：由于依指数变化，a的轻微变化会对概率有很大影响
    '''
    p0 = 0
    for _ in range(10):
        p0 = (p0 - 1) / a + 1
        print(p0)
