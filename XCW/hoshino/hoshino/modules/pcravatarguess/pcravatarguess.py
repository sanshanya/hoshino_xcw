from nonebot import MessageSegment

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.modules.priconne import chara
from hoshino.modules.priconne import _pcr_data

import hoshino
import math, sqlite3, os, random, asyncio


sv = Service('avatarguess', bundle='pcr娱乐', help_='''
猜头像 | 猜猜机器人随机发送的头像的一小部分来自哪位角色
猜头像群排行 | 显示猜头像小游戏猜对次数的群排行榜(只显示前十名)
'''.strip())


PIC_SIDE_LENGTH = 25 
ONE_TURN_TIME = 20
DB_PATH = os.path.expanduser('~/.hoshino/pcr_avatar_guess_winning_counter.db')
BLACKLIST_ID = [1072, 1908, 4031, 9000]

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
        self.correct_chara_id[gid] = chara.UNKNOWN


winner_judger = WinnerJudger()


class WinningCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS WINNINGCOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           COUNT           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    
    
    def _record_winning(self, gid, uid):
        try:
            winning_number = self._get_winning_number(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO WINNINGCOUNTER (GID,UID,COUNT) \
                                VALUES (?,?,?)", (gid, uid, winning_number+1))
            conn.commit()       
        except:
            raise Exception('更新表发生错误')


    def _get_winning_number(self, gid, uid):
        try:
            r = self._connect().execute("SELECT COUNT FROM WINNINGCOUNTER WHERE GID=? AND UID=?",(gid,uid)).fetchone()        
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card']!='' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]


@sv.on_fullmatch(('猜头像排行榜', '猜头像群排行'))
async def description_guess_group_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        card_winningcount_dict = {}
        winning_counter = WinningCounter()
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                card_winningcount_dict[user_card_dict[uid]] = winning_counter._get_winning_number(ev.group_id, uid)
        group_ranking = sorted(card_winningcount_dict.items(), key = lambda x:x[1], reverse = True)
        msg = '猜头像小游戏此群排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i+1}名: {group_ranking[i][0]}, 猜对次数: {group_ranking[i][1]}次\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch('猜头像')
async def avatar_guess(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        winner_judger.turn_on(ev.group_id)
        chara_id_list = list(_pcr_data.CHARA_NAME.keys())
        while True:
            random.shuffle(chara_id_list)
            if chara_id_list[0] not in BLACKLIST_ID: break
        winner_judger.set_correct_chara_id(ev.group_id, chara_id_list[0])
        dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'priconne', 'unit')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        c = chara.fromid(chara_id_list[0])
        img = c.icon.open()
        left = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
        upper = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
        cropped = img.crop((left, upper, left+PIC_SIDE_LENGTH, upper+PIC_SIDE_LENGTH))
        file_path = os.path.join(dir_path, 'cropped_avatar.png')
        cropped.save(file_path)
        image = MessageSegment.image(f'file:///{os.path.abspath(file_path)}')   
        msg = f'猜猜这个图片是哪位角色头像的一部分?({ONE_TURN_TIME}s后公布答案){image}'
        await bot.send(ev, msg)
        await asyncio.sleep(ONE_TURN_TIME)
        if winner_judger.get_winner(ev.group_id) != '':
            winner_judger.turn_off(ev.group_id)
            return
        msg =  f'正确答案是: {c.name}{c.icon.cqcode}\n很遗憾，没有人答对~'
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
    except Exception as e:
        winner_judger.turn_off(ev.group_id)
        await bot.send(ev, '错误:\n' + str(e))
        
        
@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            s = ev.message.extract_plain_text()
            cid = chara.name2id(s)
            if cid != chara.UNKNOWN and cid == winner_judger.get_correct_chara_id(ev.group_id) and winner_judger.get_winner(ev.group_id) == '':
                winner_judger.record_winner(ev.group_id, ev.user_id)
                winning_counter = WinningCounter()
                winning_counter._record_winning(ev.group_id, ev.user_id)
                winning_count = winning_counter._get_winning_number(ev.group_id, ev.user_id)
                user_card_dict = await get_user_card_dict(bot, ev.group_id)
                user_card = uid2card(ev.user_id, user_card_dict)
                msg_part = f'{user_card}猜对了，真厉害！TA已经猜对{winning_count}次了~\n(此轮游戏将在时间到后自动结束，请耐心等待)'
                c = chara.fromid(winner_judger.get_correct_chara_id(ev.group_id))
                msg =  f'正确答案是: {c.name}{c.icon.cqcode}\n{msg_part}'
                await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))