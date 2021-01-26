from hoshino.typing import CQEvent
from hoshino import Service, priv, R
import math, sqlite3, os, random, asyncio, hoshino, requests
from nonebot import MessageSegment
from hoshino.util import DailyNumberLimiter

sv_help = '''
- [猜群友] 猜猜机器人随机发送的头像的一小部分来自哪位群友
'''.strip()

sv = Service(
    name = '猜群友',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助猜群友"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


BLACKLIST_ID = [1000]
PIC_SIDE_LENGTH = 30
ONE_TURN_TIME = 30
DB_PATH = r'~/.hoshino/winning_counter.db' 
lmt = DailyNumberLimiter(10)

class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}

    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)

    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid

    def get_correct_chara_id(self, gid):
        return self.correct_chara_id[gid] if self.correct_chara_id.get(gid) is not None else chara.UNKNOWN

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = '00000000'


winner_judger = WinnerJudger()


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card'] != '' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]



@sv.on_fullmatch('猜群友')
async def avatar_guess(bot, ev: CQEvent):
    try:
        uid = ev.user_id
        if winner_judger.get_on_off_status(ev.group_id):
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        if not lmt.check(uid):
            await bot.send(ev, '您今天已经玩了10次猜群友了，休息一下，明天再来吧！', at_sender=True)
            return
        lmt.increase(uid)
        winner_judger.turn_on(ev.group_id)

        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        user_id_list = list(user_card_dict.keys())
        while True:
            random.shuffle(user_id_list)
            if user_id_list[0] !=ev.self_id: break
        winner_judger.set_correct_chara_id(ev.group_id, user_id_list[0])
        dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'memavatar')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        apiPath=f' http://q1.qlogo.cn/g?b=qq&nk={user_id_list[0]}&s=100'
        img = requests.get(apiPath, timeout=20).content
        ava_path = os.path.join(dir_path, f'{ev.group_id}_memavatar.png')
        with open(ava_path, 'wb') as f:
            f.write(img)

        avaimg = R.img(f'{os.path.abspath(ava_path)}').open()
        avaimage = MessageSegment.image(f'file:///{os.path.abspath(ava_path)}')
        left = math.floor(random.random() * (100 - PIC_SIDE_LENGTH))
        upper = math.floor(random.random() * (100 - PIC_SIDE_LENGTH))
        cropped = avaimg.crop((left, upper, left + PIC_SIDE_LENGTH, upper + PIC_SIDE_LENGTH))
        file_path = os.path.join(dir_path, f'{ev.group_id}_cropped_memavatar.png')
        cropped.save(file_path)
        image = MessageSegment.image(f'file:///{os.path.abspath(file_path)}')
        msg = f'猜猜这个图片是哪位群友头像的一部分?({ONE_TURN_TIME}s后公布答案){image}'
        await bot.send(ev, msg)
        await asyncio.sleep(ONE_TURN_TIME)

        if winner_judger.get_winner(ev.group_id) != '':
            winner_judger.turn_off(ev.group_id)
            return

        msg = f'正确答案是: {user_card_dict[user_id_list[0]]}{avaimage}\n很遗憾，没有人答对~'
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
    except Exception as e:
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            for m in ev.message:
                if m.type == 'at' and m.data['qq'] != 'all':
                    atuid = int(m.data['qq'])
                    info = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=atuid)
                    card =  info['card']
                    nickname =  info['nickname']
                    s = card
                    if card == '' :
                        s = nickname
                    #await bot.send(ev, f'at解析为{s}')
                    break
                else:
                    s = ev.message.extract_plain_text()
                    break
            cid = winner_judger.get_correct_chara_id(ev.group_id)
            info = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=cid)
            card =  info['card']
            nickname =  info['nickname']
            #await bot.send(ev, f'匹配对象{s}，匹配目标{card}、{nickname}')
            if (s == card or s == nickname) and winner_judger.get_winner(ev.group_id) == '':
                winner_judger.record_winner(ev.group_id, ev.user_id)
                winnerinfo = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=ev.user_id)
                winnercard =  winnerinfo['card']
                if winnercard ==  '':
                    winnercard =  winnerinfo['nickname']
                msg_part = f'{winnercard}猜对了，真厉害！\n(此轮游戏将在时间到后自动结束，请耐心等待)'

                dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'memavatar')
                ava_path = os.path.join(dir_path, f'{ev.group_id}_memavatar.png')
                avaimg = R.img(f'{os.path.abspath(ava_path)}')
                avaimage = MessageSegment.image(f'file:///{os.path.abspath(ava_path)}')
                if card ==  '':
                    card =  nickname
                msg = f'正确答案是: {card}{avaimage}\n{msg_part}'
                await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))
