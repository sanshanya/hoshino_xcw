from hoshino import Service, priv, jewel
from hoshino.typing import CQEvent
from hoshino.modules.priconne import chara
from . import _chara_data

import hoshino
import sqlite3, os, random, asyncio

sv_help = '''
- [猜角色] 猜猜机器人随机发送的文本在描述哪位角色
- [猜角色群排行] 显示猜角色小游戏猜对次数的群排行榜(只显示前十名)
'''.strip()

sv = Service(
    name = '猜角色',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助猜角色"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)



PREPARE_TIME = 5
ONE_TURN_TIME = 12
TURN_NUMBER = 5
DB_PATH = os.path.expanduser('~/.hoshino/pcr_desc_guess_winning_counter.db')


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

    
def get_cqcode(chara_id):
    dir_path = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'priconne', 'unit')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    c = chara.fromid(chara_id)
    cqcode = '' if not c.icon.exist else c.icon.cqcode
    return c.name, cqcode


@sv.on_fullmatch(('猜角色排行榜', '猜角色群排行'))
async def description_guess_group_ranking(bot, ev: CQEvent):
    try:
        user_card_dict = await get_user_card_dict(bot, ev.group_id)
        card_winningcount_dict = {}
        winning_counter = WinningCounter()
        for uid in user_card_dict.keys():
            if uid != ev.self_id:
                card_winningcount_dict[user_card_dict[uid]] = winning_counter._get_winning_number(ev.group_id, uid)
        group_ranking = sorted(card_winningcount_dict.items(), key = lambda x:x[1], reverse = True)
        msg = '猜角色小游戏此群排行为:\n'
        for i in range(min(len(group_ranking), 10)):
            if group_ranking[i][1] != 0:
                msg += f'第{i+1}名: {group_ranking[i][0]}, 猜对次数: {group_ranking[i][1]}次\n'
        await bot.send(ev, msg.strip())
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch(('猜角色', '猜人物'))
async def description_guess(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        winner_judger.turn_on(ev.group_id)
        await bot.send(ev, f'{PREPARE_TIME}秒钟后每隔{ONE_TURN_TIME}秒我会给出某位角色的一个描述，根据这些描述猜猜她是谁~')
        await asyncio.sleep(PREPARE_TIME)
        desc_lable = ['名字', '公会', '生日', '年龄', '身高', '体重', '血型', '种族', '喜好', '声优']
        desc_suffix = ['', '', '', '', 'cm', 'kg', '', '', '', '']
        index_list = list(range(1,10))
        random.shuffle(index_list)
        chara_id_list = list(_chara_data.CHARA_DATA.keys())
        random.shuffle(chara_id_list)
        chara_id = chara_id_list[0]
        chara_desc_list = _chara_data.CHARA_DATA[chara_id]
        winner_judger.set_correct_chara_id(ev.group_id, chara_id)
        for i in range(TURN_NUMBER):
            desc_index = index_list[i]
            await bot.send(ev, f'提示{i+1}/{TURN_NUMBER}:\n她的{desc_lable[desc_index]}是 {chara_desc_list[desc_index]}{desc_suffix[desc_index]}')
            await asyncio.sleep(ONE_TURN_TIME)
            if winner_judger.get_winner(ev.group_id) != '':
                winner_judger.turn_off(ev.group_id)
                return
        msg_part = '很遗憾，没有人答对~'
        name, cqcode = get_cqcode(winner_judger.get_correct_chara_id(ev.group_id))
        msg =  f'正确答案是: {name}{cqcode}\n{msg_part}'
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
                msg_part = f'{user_card}猜对了，真厉害！TA已经猜对{winning_count}次了~\n(此轮游戏将在几秒后自动结束，请耐心等待)'
                name, cqcode = get_cqcode(winner_judger.get_correct_chara_id(ev.group_id))
                jewel_counter = jewel.jewelCounter()
                winning_jewel = 50
                jewel_counter._add_jewel(ev.group_id, ev.user_id, winning_jewel)
                msg_part2 = f'{user_card}获得了{winning_jewel}宝石'
                msg =  f'正确答案是: {name}{cqcode}\n{msg_part}\n{msg_part2}'
                await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))