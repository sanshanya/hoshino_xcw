import os
import random
from collections import defaultdict
import re

from hoshino import Service, priv, util
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from .. import chara
from .gacha import Gacha
from .update import *
try:
    import ujson as json
except:
    import json

sv_help = '''
[@Bot十连] 转蛋模拟
[@Bot来发单抽] 转蛋模拟
[@Bot来一井] 4w5钻！
[查看卡池] 模拟卡池&出率
[切换卡池] 更换模拟卡池
[氪金@某人] 为某人氪金, 恢复抽卡次数
'''.strip()
sv = Service('gacha', help_=sv_help, bundle='pcr娱乐')
jewel_limit = DailyNumberLimiter(15000)
tenjo_limit = DailyNumberLimiter(5)

JEWEL_EXCEED_NOTICE = f'您今天已经抽过{jewel_limit.max}钻了，欢迎明早5点后再来！'
TENJO_EXCEED_NOTICE = f'您今天已经抽过{tenjo_limit.max}张天井券了，欢迎明早5点后再来！'
POOL = ('MIX', 'JP', 'TW', 'BL')
DEFAULT_POOL = POOL[0]

_pool_config_file = os.path.expanduser('~/.hoshino/group_pool_config.json')
_group_pool = {}
try:
    with open(_pool_config_file, encoding='utf8') as f:
        _group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('group_pool_config.json not found, will create when needed.')
_group_pool = defaultdict(lambda: DEFAULT_POOL, _group_pool)

def dump_pool_config():
    with open(_pool_config_file, 'w', encoding='utf8') as f:
        json.dump(_group_pool, f, ensure_ascii=False)


gacha_10_aliases = ('抽十连', '十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连')
gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋')
gacha_300_aliases = ('抽一井', '来一井', '来发井', '抽发井', '天井扭蛋', '扭蛋天井')

@sv.on_fullmatch(('卡池资讯', '查看卡池', '看看卡池', '康康卡池','看看up', '看看UP'))
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    up_chara = gacha.up
    up_chara = map(lambda x: str(
        chara.fromname(x, star=3).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%\n")


POOL_NAME_TIP = '请选择以下卡池\n> 选择卡池 jp\n> 选择卡池 tw\n> 选择卡池 bilibili\n> 选择卡池 fes\n> 选择卡池 七冠\n> 选择卡池 联动\n> 选择卡池 限定（现已全部实装）\n> 选择卡池 mix'
@sv.on_prefix(('切换卡池', '选择卡池'))
async def set_pool(bot, ev: CQEvent):
    #if not priv.check_priv(ev, priv.ADMIN):
    #    await bot.finish(ev, '只有群管理才能切换卡池', at_sender=True)
    name = util.normalize_str(ev.message.extract_plain_text())
    if not name:
        await bot.finish(ev, POOL_NAME_TIP, at_sender=True)
    elif name in ('国', '国服', 'cn'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 b服\n> 选择卡池 台服')
    elif name in ('b', 'b服', 'bl', 'bilibili'):
        name = 'BL'
    elif name in ('台', '台服', 'tw', 'sonet'):
        name = 'TW'
    elif name in ('日', '日服', 'jp', 'cy', 'cygames'):
        name = 'JP'
    elif name in ('fes', '盛典'):
        name = 'FES'
    elif name in ('七冠', 'セブンクラウンズ'):
        name = 'セブンクラウンズ'    
    elif name in ('联动', '活动'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 re0\n> 选择卡池 偶像大师')
    elif name in ('RE:0联动', 're0联动', 're0'):
        name = 're0'
    elif name in ('偶像大师联动', '偶像大师活动', '偶像大师'):
        name = '偶像大师'
    elif name in ('限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 泳装限定\n> 选择卡池 万圣限定\n> 选择卡池 圣诞限定\n> 选择卡池 春节限定\n> 选择卡池 情人节限定')
    elif name in ('泳装限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 泳装佩可\n> 选择卡池 泳装铃莓\n> 选择卡池 泳装凯露\n> 选择卡池 泳装珠希\n> 选择卡池 泳装铃奈\n> 选择卡池 泳装咲恋\n> 选择卡池 泳装真琴\n> 选择卡池 泳装真步\n> 选择卡池 泳装流夏')
    elif name in ('泳装佩可', '泳装吃货', '水吃'):
        name = '泳裝-佩可'
    elif name in ('泳装铃莓', '泳装女仆', '水女仆'):
        name = '泳裝-鈴莓'
    elif name in ('泳装凯露', '泳装黑猫', '水黑'):
        name = '泳裝-凱留'
    elif name in ('泳装珠希', '泳装猫剑', '水猫剑'):
        name = '泳裝-珠希'
    elif name in ('泳装铃奈', '泳装暴击弓', '水暴', '瀑'):
        name = '泳裝-鈴奈'
    elif name in ('泳装咲恋', '泳装充电宝', '水电'):
        name = '泳裝-咲戀'
    elif name in ('泳装真琴', '泳装狼', '水狼', '浪'):
        name = '泳裝-真琴'
    elif name in ('泳装真步', '泳装狐狸', '水狐', '水壶'):
        name = '泳裝-真步'
    elif name in ('泳装流夏', '泳装大姐头', '水流夏', '水大姐头'):
        name = '泳裝-流夏'
    elif name in ('泳装纯', '泳装黑骑','水纯'):
        name = '泳裝-纯'
    elif name in ('万圣限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 万圣忍\n> 选择卡池 万圣美咲\n> 选择卡池 万圣小仓唯')
    elif name in ('万圣忍', '瓜忍'):
        name = '萬聖節-忍'
    elif name in ('万圣美咲', '万圣大眼', '瓜眼'):
        name = '萬聖節-美咲'
    elif name in ('万圣小仓唯', 'mcw', '猫唯'):
        name = '萬聖節-鏡華'
    elif name in ('圣诞限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 圣诞千歌\n> 选择卡池 圣诞绫音\n> 选择卡池 圣诞克里斯蒂娜')
    elif name in ('圣诞千歌', '圣千'):
        name = '聖誕節-千歌'
    elif name in ('圣诞绫音', '圣诞熊锤'):
        name = '聖誕節-綾音'
    elif name in ('圣诞克里斯蒂娜', '圣克', '蛋壳'):
        name = '聖誕節-克莉絲蒂娜'
    elif name in ('春节限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 新年优衣\n> 选择卡池 新年日和\n> 选择卡池 正月凯露\n> 选择卡池 正月可可萝')
    elif name in ('新年优衣', '春田'):
        name = '新年-優衣'
    elif name in ('新年日和', '春猫'):
        name = '新年-日和'
    elif name in ('正月凯露', '春黑', '唯一的神'):
        name = '正月-凱留'
    elif name in ('正月可可萝', '春妈'):
        name = '正月-可可蘿'
    elif name in ('情人节限定'):
        await bot.finish(ev,'请选择以下卡池\n> 选择卡池 情人节静流')
    elif name in ('情人节静流', '情姐'):
        name = '情人節-靜流'
    elif name in ('混', '混合', 'mix'):
        name = 'MIX'
    else:
        await bot.finish(ev, f'未知卡池 {POOL_NAME_TIP}', at_sender=True)
    gid = str(ev.group_id)
    _group_pool[gid] = name
    dump_pool_config()
    await bot.send(ev, f'卡池已切换为{name}池', at_sender=True)
    await gacha_info(bot, ev)


async def check_jewel_num(bot, ev: CQEvent):
    if not jewel_limit.check(ev.user_id):
        await bot.finish(ev, JEWEL_EXCEED_NOTICE, at_sender=True)


async def check_tenjo_num(bot, ev: CQEvent):
    if not tenjo_limit.check(ev.user_id):
        await bot.finish(ev, TENJO_EXCEED_NOTICE, at_sender=True)


@sv.on_prefix(gacha_1_aliases, only_to_me=True)
async def gacha_1(bot, ev: CQEvent):

    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 150)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    # silence_time = hiishi * 60

    res = f'{chara.name} {"★"*chara.star}'
    res = f'{chara.icon.cqcode} {res}'

    # await silence(ev, silence_time)
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_prefix(gacha_10_aliases, only_to_me=True)
async def gacha_10(bot, ev: CQEvent):
    SUPER_LUCKY_LINE = 170

    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 1500)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    result, hiishi = gacha.gacha_ten()
    # silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60


    res1 = chara.gen_team_pic(result[:5], star_slot_verbose=False)
    res2 = chara.gen_team_pic(result[5:], star_slot_verbose=False)
    res = concat_pic([res1, res2])
    res = pic2b64(res)
    res = MessageSegment.image(res)
    result = [f'{c.name}{"★"*c.star}' for c in result]
    res1 = ' '.join(result[0:5])
    res2 = ' '.join(result[5:])
    res = f'{res}\n{res1}\n{res2}'


    if hiishi >= SUPER_LUCKY_LINE:
        await bot.send(ev, '恭喜海豹！おめでとうございます！')
    await bot.send(ev, f'素敵な仲間が増えますよ！\n{res}\n', at_sender=True)
    #await silence(ev, silence_time)


@sv.on_prefix(gacha_300_aliases, only_to_me=True)
async def gacha_300(bot, ev: CQEvent):

    await check_tenjo_num(bot, ev)
    tenjo_limit.increase(ev.user_id)

    gid = str(ev.group_id)
    gacha = Gacha(_group_pool[gid])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        f"\n素敵な仲間が増えますよ！ {res}",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{100*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")

    await bot.send(ev, '\n'.join(msg), at_sender=True)
    #silence_time = (100*up + 50*(up+s3) + 10*s2 + s1) * 1
    #await silence(ev, silence_time)


@sv.on_prefix('氪金')
async def kakin(bot, ev: CQEvent):
    #if ev.user_id not in bot.config.SUPERUSERS:
    #    return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")
