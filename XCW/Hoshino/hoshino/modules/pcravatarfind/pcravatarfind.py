import random, os, sqlite3, asyncio, operator, re
from PIL import Image

import hoshino
from hoshino import Service, priv, util, log, R, jewel
from hoshino.modules.priconne import chara
from hoshino.typing import MessageSegment, CQEvent

from . import GameMaster

sv_help = '''
-[找头像]  找出一堆头像中的不同头像
-[找头像群排行]  显示找头像小游戏猜对次数的群排行榜(只显示前十名)
'''.strip()

sv = Service(
    name = '找头像',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助找头像"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)



SUB_PIC_SIZE = 128
DB_PATH = os.path.expanduser('~/.hoshino/cat_guess_winning_counter.db')
gm = GameMaster(DB_PATH)

    
def get_merge_avatar():
    num = random.randint(5,25) #难度
    ONE_TURN_TIME = (num-1)*2  #时间
    choose = random.randint(1,5) #选择近似头像
    if choose==1:
        avatar1 = R.img(f'priconne/unit/icon_unit_170111.png').open() #环奈
        avatar2 = R.img(f'priconne/unit/icon_unit_170211.png').open() #春奈
    elif choose==2:
        avatar2 = R.img(f'priconne/unit/icon_unit_102711.png').open() #病娇
        avatar1 = R.img(f'priconne/unit/icon_unit_109031.png').open() #情娇
    elif choose==3:
        avatar1 = R.img(f'priconne/unit/icon_unit_104311.png').open() #狼
        avatar2 = R.img(f'priconne/unit/icon_unit_110411.png').open() #水狼
    elif choose==4:
        avatar1 = R.img(f'priconne/unit/icon_unit_108111.png').open() #瓜忍
        avatar2 = R.img(f'priconne/unit/icon_unit_103111.png').open() #忍
    elif choose==5:
        avatar1 = R.img(f'priconne/unit/icon_unit_107611.png').open() #水妈
        avatar2 = R.img(f'priconne/unit/icon_unit_105911.png').open() #妈
    w = num * SUB_PIC_SIZE
    h = num * SUB_PIC_SIZE
    base = Image.new('RGBA', (h, w), (255, 255, 255, 255))
    coordinate = 0
    coordinate1 = 1
    for i in range(num+1):
        for j in range(num+1):
            if j == 0 :
                avatar3 = R.img(f'priconne/find/icon_unit_{coordinate}.png').open()
                base.paste(avatar3,(j*SUB_PIC_SIZE,i*SUB_PIC_SIZE))     
                coordinate += 1
            elif i == 0:
                avatar3 = R.img(f'priconne/find/icon_unit_{coordinate1}.png').open()
                base.paste(avatar3,(j*SUB_PIC_SIZE,i*SUB_PIC_SIZE))     
                coordinate1 += 1
            else:
                base.paste(avatar1,(j*SUB_PIC_SIZE,i*SUB_PIC_SIZE))     
    x = random.randint(1,num-1)
    y = random.randint(1,num-1)
    base.paste(avatar2,(x*SUB_PIC_SIZE,y*SUB_PIC_SIZE))
    coordinate = (x,y)
    base.thumbnail((w//2,h//2))
    return coordinate,base,ONE_TURN_TIME

@sv.on_fullmatch(("找头像排行", "找头像排名","找头像排行榜", "找头像群排行"))
async def description_find_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【找头像小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(
            self_id=ev.self_id, group_id=ev.group_id, user_id=uid
        )
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名：{name} 猜对{count}次")
    await bot.send(ev, "\n".join(msg))
   
@sv.on_fullmatch('找头像')
async def avatar_find(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        game.answer,answer_pic,ONE_TURN_TIME = get_merge_avatar()
        answer_pic = MessageSegment.image(util.pic2b64(answer_pic))
        await bot.send(ev, f'请找出不一样的头像坐标?({ONE_TURN_TIME}s后公布答案){answer_pic}')
        await asyncio.sleep(ONE_TURN_TIME)
        if game.winner:
            return
    await bot.send(ev, f'正确答案是: {game.answer}\n很遗憾，没有人答对~')
        
        
@sv.on_message()
async def on_input_coordinate(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.winner:
        return
    #匹配输入，正确内容转换为元组
    s = ev.message.extract_plain_text()
    if not re.match(r'^(?:\(|（)\d+(?:\,|，)\d+(?:\)|）)$',s):
        return
    temp=s.replace('(','').replace(')','').replace('（','').replace('）','').replace('，',',')
    answer=tuple([int(i) for i in temp.split(',')])

    if operator.eq(answer,game.answer):
        game.winner = ev.user_id
        n = game.record()
        msg_part = f'{MessageSegment.at(ev.user_id)}猜对了，真厉害！TA已经猜对{n}次了~\n(此轮游戏将在时间到后自动结束，请耐心等待)'
        jewel_counter = jewel.jewelCounter()
        winning_jewel = 60
        jewel_counter._add_jewel(ev.group_id, ev.user_id, winning_jewel)
        msg_part2 = f'{ev.user_id}获得了{winning_jewel}宝石'
        msg =  f'正确坐标是: {game.answer}\n{msg_part}\n{msg_part2}'
        await bot.send(ev, msg)