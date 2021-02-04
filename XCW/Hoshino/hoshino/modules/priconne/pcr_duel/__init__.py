import asyncio
import base64
import os
import random
import sqlite3
import math
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
from hoshino import Service, priv, jewel
from hoshino.modules.priconne import _pcr_data_dlc as _pcr_data
from hoshino.modules.priconne import chara_dlc as chara
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter
import copy
import json

sv_help = '''
- [贵族帮助]
- [声望系统帮助] 
- [国王的遗书]
- [国王的羊皮纸]
- [骑士的转生手册]
- [dlc帮助]
'''.strip()

sv = Service(
    name = '贵族决斗',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助贵族决斗"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help)
    
DUEL_DB_PATH = os.path.expanduser('~/.hoshino/pcr_duel.db')
SCORE_DB_PATH = os.path.expanduser('~/.hoshino/pcr_running_counter.db')
BLACKLIST_ID = [1000, 1072, 1908, 9000, 1069,1913,1916,1917,1918,1919,1920,9601,9602,9603,9604]# 黑名单ID
WAIT_TIME = 30 # 对战接受等待时间
DUEL_SUPPORT_TIME = 30 # 赌钱等待时间
DB_PATH = os.path.expanduser("~/.hoshino/pcr_duel.db")
SIGN_DAILY_LIMIT = 1  # 机器人每天签到的次数
DUEL_DAILY_LIMIT = 30 #每个人每日发起决斗上限
QIDAO_DAILY_LIMIT = 10 #祈祷上限
CHONGSHENG_DAILY_LIMIT = 3 #重生上限
RESET_HOUR = 0  # 每日使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推
GACHA_COST = 3000  # 抽老婆需求
ZERO_GET_AMOUNT = 500  # 没钱补给量
WIN_NUM = 1 #下注获胜赢得的倍率
BREAK_UP_SWITCH = True #分手系统开关
SELLMA = True #卖女友开关
FILE_PATH = os.path.dirname(__file__)#用于加载dlcjson

LEVEL_GIRL_NEED = {
        "1": 2,
        "2": 4,
        "3": 6,
        "4": 8,
        "5": 12,
        "6": 14,
        "7": 20
    } # 升级所需要的老婆，格式为["等级“: 需求]
LEVEL_COST_DICT = {
        "1": 0,
        "2": 1000,
        "3": 3000,
        "4": 50000,
        "5": 700000,
        "6": 9000000
    } # 升级所需要的钱钱，格式为["等级“: 需求]
Addgirlfail = [
    '你参加了一场贵族舞会，热闹的舞会场今天竟然没人同你跳舞',
    '你邀请到了心仪的女友跳舞，可是跳舞时却踩掉了她的鞋，她生气的离开了',
    '你为这次舞会准备了很久，结果一不小心在桌子上睡着了，醒来时只看到了过期的邀请函',
    '你参加了一场贵族舞会，可是舞会上只有一名男性向你一直眨眼',
    '你准备参加一场贵族舞会，可惜因为忘记穿礼服，被拦在了门外',
    '你沉浸在舞会的美食之中，忘了此行的目的',
    '你本准备参加舞会，却被会长拉去出了一晚上刀',
    '舞会上你和另一个贵族发生了争吵，你一拳打破了他的鼻子，两人都被请出了舞会',
    '舞会上你很快约到了一名女伴跳舞，但是她不是你喜欢的类型',
    '你约到了一位心仪的女伴，但是她拒绝了与你回家，说想再给你一个考验',
    '你和另一位贵族同时看中了一个女孩，但是在三人交谈时，你渐渐的失去了话题'
]
Addgirlsuccess = [
    '你参加了一场贵族舞会，你优雅的舞姿让每位年轻女孩都望向了你',
    '你参加了一场贵族舞会，你的帅气使你成为了舞会的宠儿',
    '你在舞会门口就遇到了一位女孩，你挽着她的手走进了舞会',
    '你在舞会的闲聊中无意中谈到了自己显赫的家室，你成为了舞会的宠儿',
    '没有人比你更懂舞会，每一个女孩都为你的风度倾倒',
    '舞会上你没有约到女伴，但是舞会后却有个女孩偷偷跟着你回了家',
    '舞会上你和另一个贵族发生了争吵，一位女孩站出来为你撑腰，你第一次的注意到了这个可爱的女孩',
    '你强壮的体魄让女孩们赞叹不已，她们纷纷来问你是不是一位军官',
    '你擅长在舞会上温柔地对待每一个人，女孩们也向你投来了爱意',
    '一个可爱的女孩一直在舞会上望着你，你犹豫了一会，向她发出了邀请'
  
]

Login100 =[
    '今天是练习击剑的一天，不过你感觉你的剑法毫无提升',
    '优雅的贵族从不晚起，可是你今天一直睡到了中午',
    '今天你点了一份豪华的午餐却忘记了带钱，窘迫的你毫无贵族的姿态',
    '今天你在路上看上了别人的女友，却没有鼓起勇气向他决斗',
    '今天你十分抑郁，因为发现自己最近上升的只有体重'

]

Login200 =[
    '今天是练习击剑的一天，你感觉到了你的剑法有所提升',
    '早起的你站在镜子前许久，天底下竟然有人可以这么帅气',
    '今天你搞到了一瓶不错的红酒，你的酒窖又多了一件存货',
    '今天巡视领地时，一个小孩子崇拜地望着你，你感觉十分开心',
    '今天一个朋友送你一张音乐会的门票，你打算邀请你的女友同去',
    '今天一位国王的女友在路上向你抛媚眼，也许这就是个人魅力吧'
    
]


Login300 =[
    '今天是练习击剑的一天，你感觉到了你的剑法大有长进',
    '今天你救下了一个落水的小孩，他的家人说什么也要你收下一份心意',
    '今天你巡视领地时，听到几个小女孩说想长大嫁给帅气的领主，你心里高兴极了',
    '今天你打猎时猎到了一只鹿，你骄傲的把鹿角加入了收藏',
    '今天你得到了一匹不错的马，说不定可以送去比赛'
    
]

Login600 =[
    '今天是练习击剑的一天，你觉得自己已经可谓是当世剑圣',
    '今天你因为领地治理有方，获得了皇帝的嘉奖',
    '今天你的一位叔叔去世了，无儿无女的他，留给了你一大笔遗产',
    '今天你在比武大会上获得了优胜，获得了全场的喝彩',
    '今天你名下的马夺得了赛马的冠军，你感到无比的自豪'
    
    
]
@sv.on_fullmatch(['贵族决斗帮助','贵族帮助','贵族指令'])
async def duel_help(bot, ev: CQEvent):
    msg='''
╔                                       ╗    
    贵族决斗相关指令
   1.贵族签到(每日一次)
   2.查询贵族
   3.贵族决斗+艾特
   4.领金币/查金币
   5.贵族舞会(招募女友)
   6.查女友+角色名
   7.升级贵族
   8.重置决斗(限管理，决
   斗卡住时用)
   9.分手+角色名(需分手费)
╚                                        ╝
'''  
    data ={
            "type": "node",
            "data": {
                "name": '贵族小冰',
                "uin": '2854196306',
                "content": msg
            }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data)

@sv.on_fullmatch(['国王的遗书'])
async def duel_help_guowang(bot, ev: CQEvent):
    msg='''
╔                                       ╗    
    这是吾登上国王之位的经验:
   1.招募女友的费用与女友数有关
   2.前期收益最高的是[贵族祈祷]
   3.贵族每天的薪酬与女友数有关
   4.前期开局不好可以重生
   5.招募女友成功与失败概率大概对半开
   6.决斗如果一方不开枪认输双方都得不了钱
   7.登上了国王宝座后这个游戏才刚开始
   8.当女友数满时决斗可以获取[巨量]金币
   9.决斗的收益随爵位[指数增长]
   10.尽早[开启声望系统]
╚                                        ╝
'''  
    data ={
            "type": "node",
            "data": {
                "name": '贵族小冰',
                "uin": '2854196306',
                "content": msg
            }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data)

@sv.on_fullmatch(['骑士的转生手册'])
async def duel_help_qishi(bot, ev: CQEvent):
    msg='''
╔                                       ╗    
   [贵族转生]次数有限
   [重置金币]却是无限的
   转生后声望系统会保留
   [宝石兑换声望 XX]
   [声望兑换宝石 XX]
   宝石和声望是1：1的关系
   但是宝石从哪里来呢？
╚                                        ╝
'''  
    data ={
            "type": "node",
            "data": {
                "name": '贵族小冰',
                "uin": '2854196306',
                "content": msg
            }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data)

@sv.on_fullmatch(['国王的羊皮纸'])
async def duel_help_mowang(bot, ev: CQEvent):
    msg='''
╔                                       ╗    
    曾经我也是虔诚的信徒
    但是我忠诚的信仰却未能得到神的回应
    我与恶魔签订了契约
    通过不断买卖女友获取金币
    - [卖女友+角色名]
    卖女友能获得的钱随爵位指数增长
    而买女友的金币是随女友数增长
    我可以从中获取足够的金钱
    - [金币兑换声望 XX]
    - [兑换金币声望 XX]
    钱即是荣誉
    但与恶魔交易是有风险的
    每一次交易
    我都感觉我得到的只是
    梦幻泡影
    ......
    一将功成万骨枯
    我已经下定决心
╚                                        ╝
'''  
    data ={
            "type": "node",
            "data": {
                "name": '贵族小冰',
                "uin": '2854196306',
                "content": msg
            }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data)


#加载DLC部分代码
#这里记录每个dlc的列表范围

blhxlist = range(6000,6506)
yozilist = range(1523,1544)
genshinlist = range(7001,7018)
bangdreamlist = range(1601,1636)


#这里记录dlc名字和对应列表
dlcdict = {
        'blhx':blhxlist,
        'yozi':yozilist,
        'genshin':genshinlist,
        'bangdream':bangdreamlist
        }


#这里记录每个dlc的介绍
dlcintro = {
        'blhx':'碧蓝航线手游角色包。',
        'yozi':'柚子社部分角色包。',
        'genshin':'原神角色包。',
        'bangdream':'邦邦手游角色包。'
        }




# 这个字典保存保存每个DLC开启的群列表，pcr默认一直开启。
dlc_switch={}

with open(os.path.join(FILE_PATH,'dlc_config.json'),'r',encoding='UTF-8') as f:
    dlc_switch = json.load(f, strict=False)
def save_dlc_switch():
    with open(os.path.join(FILE_PATH,'dlc_config.json'),'w',encoding='UTF-8') as f:
        json.dump(dlc_switch,f,ensure_ascii=False)



@sv.on_prefix(['加载dlc','加载DLC','开启dlc','开启DLC'])
async def add_dlc(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能加载dlc哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args)>= 2:
        await bot.finish(ev, '指令格式错误。', at_sender=True)
    if len(args)==0:
        await bot.finish(ev, '请输入加载dlc+dlc名。', at_sender=True)
    dlcname = args[0]
    if dlcname not in dlcdict.keys():
        await bot.finish(ev, 'DLC名填写错误。', at_sender=True)        

    if gid in dlc_switch[dlcname]:
        await bot.finish(ev, '本群已开启此dlc哦。', at_sender=True)
    dlc_switch[dlcname].append(gid)
    save_dlc_switch()
    await bot.finish(ev, f'加载dlc {dlcname}  成功!', at_sender=True)



@sv.on_prefix(['卸载dlc','卸载DLC','关闭dlc','关闭DLC'])
async def delete_dlc(bot, ev: CQEvent):
    gid = ev.group_id
    if not priv.check_priv(ev, priv.OWNER):
        await bot.finish(ev, '只有群主才能卸载dlc哦。', at_sender=True)
    args = ev.message.extract_plain_text().split()
    if len(args)>= 2:
        await bot.finish(ev, '指令格式错误', at_sender=True)
    if len(args)==0:
        await bot.finish(ev, '请输入卸载dlc+dlc名。', at_sender=True)
    dlcname = args[0]
    if dlcname not in dlcdict.keys():
        await bot.finish(ev, 'DLC名填写错误', at_sender=True)        

    if gid not in dlc_switch[dlcname]:
        await bot.finish(ev, '本群没有开启此dlc哦。', at_sender=True)
    dlc_switch[dlcname].remove(gid)
    save_dlc_switch()
    await bot.finish(ev, f'卸载dlc {dlcname}  成功!', at_sender=True)



@sv.on_fullmatch(['dlc列表','DLC列表','dlc介绍','DLC介绍'])
async def intro_dlc(bot, ev: CQEvent):
    msg = '可用DLC列表：\n\n'
    i=1
    for dlc in dlcdict.keys():
        msg+=f'{i}.{dlc}:\n'
        intro = dlcintro[dlc]
        msg+=f'介绍:{intro}\n'
        num = len(dlcdict[dlc])
        msg+=f'共有{num}名角色\n\n'
        i+=1
    msg+= '发送 加载\卸载dlc+dlc名\n可加载\卸载dlc\n卸载的dlc不会被抽到，但是角色仍留在玩家仓库，可以被抢走。'    

    await bot.finish(ev, msg)

@sv.on_fullmatch(['dlc帮助','DLC帮助','dlc指令','DLC指令'])
async def help_dlc(bot, ev: CQEvent):
    msg = '''
╔                                 ╗
         DLC帮助
      
  1.加载\卸载dlc+dlc名
  2.dlc列表(查看介绍)
  
  卸载的dlc不会被抽到
  但是角色仍留在仓库
  可以被他人抢走
  
╚                                 ╝    
'''
    await bot.finish(ev, msg)




#取得该群未开启的dlc所形成的黑名单
def get_dlc_blacklist(gid):

    dlc_blacklist=[]
    for dlc in dlcdict.keys():
        if gid not in dlc_switch[dlc]:
            dlc_blacklist += dlcdict[dlc]
    return dlc_blacklist

# noinspection SqlResolve
class RecordDAO:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        with self.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS limiter"
                "(key TEXT NOT NULL, num INT NOT NULL, date INT, PRIMARY KEY(key))"
            )

    def exist_check(self, key):
        try:
            key = str(key)
            with self.connect() as conn:
                conn.execute("INSERT INTO limiter (key,num,date) VALUES (?, 0,-1)", (key,), )
            return
        except:
            return

    def get_num(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT num FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def clear_key(self, key):
        key = str(key)
        self.exist_check(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=0 WHERE key=?", (key,), )
        return

    def increment_key(self, key, num):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET num=num+? WHERE key=?", (num, key,))
        return

    def get_date(self, key):
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            r = conn.execute(
                "SELECT date FROM limiter WHERE key=? ", (key,)
            ).fetchall()
            r2 = r[0]
        return r2[0]

    def set_date(self, date, key):
        print(date)
        self.exist_check(key)
        key = str(key)
        with self.connect() as conn:
            conn.execute("UPDATE limiter SET date=? WHERE key=?", (date, key,), )
        return


db = RecordDAO(DB_PATH)


class DailyAmountLimiter(DailyNumberLimiter):
    def __init__(self, types, max_num, reset_hour):
        super().__init__(max_num)
        self.reset_hour = reset_hour
        self.type = types

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != db.get_date(key):
            db.set_date(day, key)
            db.clear_key(key)
        return bool(db.get_num(key) < self.max)

    def check10(self, key) -> bool:
        now = datetime.now(self.tz)
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        day = (now - timedelta(hours=self.reset_hour)).day
        if day != db.get_date(key):
            db.set_date(day, key)
            db.clear_key(key)
        return bool(db.get_num(key) < 10)

    def get_num(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        return db.get_num(key)

    def increase(self, key, num=1):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.increment_key(key, num)

    def reset(self, key):
        key = list(key)
        key.append(self.type)
        key = tuple(key)
        db.clear_key(key)


daily_sign_limiter = DailyAmountLimiter("sign", SIGN_DAILY_LIMIT, RESET_HOUR)

daily_duel_limiter = DailyAmountLimiter("duel", DUEL_DAILY_LIMIT, RESET_HOUR)

daily_qidao_limiter = DailyAmountLimiter("qidao", QIDAO_DAILY_LIMIT, RESET_HOUR)

daily_chongsheng_limiter = DailyAmountLimiter("chongsheng", CHONGSHENG_DAILY_LIMIT, RESET_HOUR)

# 用于与赛跑金币互通
class ScoreCounter2:
    def __init__(self):
        os.makedirs(os.path.dirname(SCORE_DB_PATH), exist_ok=True)
        self._create_table()
        self._create_pres_table()
    def _connect(self):
        return sqlite3.connect(SCORE_DB_PATH)

    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS SCORECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           SCORE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _add_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score + score))
            conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _reduce_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, current_score - score))
                conn.commit()
            else:
                conn = self._connect()
                conn.execute("INSERT OR REPLACE INTO SCORECOUNTER (GID,UID,SCORE) \
                                VALUES (?,?,?)", (gid, uid, 0))
                conn.commit()
        except:
            raise Exception('更新表发生错误')

    def _get_score(self, gid, uid):
        try:
            r = self._connect().execute("SELECT SCORE FROM SCORECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

    # 判断金币是否足够下注
    def _judge_score(self, gid, uid, score):
        try:
            current_score = self._get_score(gid, uid)
            if current_score >= score:
                return 1
            else:
                return 0
        except Exception as e:
            raise Exception(str(e))

    #记录国王声望数据
    def _create_pres_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS PRESTIGECOUNTER
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           PRESTIGE           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')

    def _set_prestige(self, gid, uid, prestige):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _get_prestige(self, gid, uid):
        try:
            r = self._connect().execute("SELECT PRESTIGE FROM PRESTIGECOUNTER WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return None if r is None else r[0]
        except:
            raise Exception('查找声望发生错误')

    def _add_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige += num
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )

    def _reduce_prestige(self, gid, uid, num):
        prestige = self._get_prestige(gid, uid)
        prestige -= num
        prestige = max(prestige,0)
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO PRESTIGECOUNTER (GID, UID, PRESTIGE) VALUES (?, ?, ?)",
                (gid, uid, prestige),
            )





   
# 记录贵族相关数据

class DuelCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DUEL_DB_PATH), exist_ok=True)
        self._create_charatable()
        self._create_uidtable()
        self._create_leveltable()
        self._create_queentable()

    def _connect(self):
        return sqlite3.connect(DUEL_DB_PATH)

    def _create_charatable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS CHARATABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建角色表发生错误')

    def _create_uidtable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS UIDTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           CID           INT    NOT NULL,
                           NUM           INT    NOT NULL,
                           PRIMARY KEY(GID, UID, CID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _create_leveltable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS LEVELTABLE
                          (GID             INT    NOT NULL,
                           UID             INT    NOT NULL,
                           LEVEL           INT    NOT NULL,
                           
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建UID表发生错误')

    def _get_card_owner(self, gid, cid):
        try:
            r = self._connect().execute("SELECT UID FROM CHARATABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找角色归属发生错误')

    def _set_card_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO CHARATABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_card_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM CHARATABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )


# 查询已被邀请的女友列表

    def _get_card_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM CHARATABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}

    def _get_level(self, gid, uid):
        try:
            r = self._connect().execute("SELECT LEVEL FROM LEVELTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找等级发生错误')

    def _get_cards(self, gid, uid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT CID, NUM FROM UIDTABLE WHERE GID=? AND UID=? AND NUM>0", (gid, uid)
            ).fetchall()
        return [c[0] for c in r] if r else {}

    def _get_card_num(self, gid, uid, cid):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT NUM FROM UIDTABLE WHERE GID=? AND UID=? AND CID=?", (gid, uid, cid)
            ).fetchone()
            return r[0] if r else 0

    def _add_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        if cid !=9999:
            self._set_card_owner(gid, cid, uid)

    def _delete_card(self, gid, uid, cid, increment=1):
        num = self._get_card_num(gid, uid, cid)
        num -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO UIDTABLE (GID, UID, CID, NUM) VALUES (?, ?, ?, ?)",
                (gid, uid, cid, num),
            )
        self._delete_card_owner(gid, cid)

    def _add_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level += increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _reduce_level(self, gid, uid, increment=1):
        level = self._get_level(gid, uid)
        level -= increment
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )

    def _set_level(self, gid, uid, level):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO LEVELTABLE (GID, UID, LEVEL) VALUES (?, ?, ?)",
                (gid, uid, level),
            )
    def _get_level_num(self, gid, level):
        with self._connect() as conn:
            r = conn.execute(
                "SELECT COUNT(UID) FROM LEVELTABLE WHERE GID=? AND LEVEL=? ", (gid, level)
            ).fetchone()
            return r[0] if r else 0   
    
  

#皇后部分

    def _create_queentable(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS QUEENTABLE
                          (GID             INT    NOT NULL,
                           CID             INT    NOT NULL,
                           UID           INT    NOT NULL,
                           PRIMARY KEY(GID, CID));''')
        except:
            raise Exception('创建皇后表发生错误')

    def _get_queen_owner(self, gid, cid):
        try:
            r = self._connect().execute("SELECT UID FROM QUEENTABLE WHERE GID=? AND CID=?", (gid, cid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找皇后归属发生错误')

    def _set_queen_owner(self, gid, cid, uid):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO QUEENTABLE (GID, CID, UID) VALUES (?, ?, ?)",
                (gid, cid, uid),
            )

    def _delete_queen_owner(self, gid, cid):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM QUEENTABLE  WHERE GID=? AND CID=?",
                (gid, cid),
            )
    def _get_queen_list(self, gid):
        with self._connect() as conn:
            r = conn.execute(
                f"SELECT CID FROM QUEENTABLE WHERE GID={gid}").fetchall()
            return [c[0] for c in r] if r else {}
#查询某人的皇后，无则返回0
    def _search_queen(self,gid,uid):
        try:
            r = self._connect().execute("SELECT CID FROM QUEENTABLE WHERE GID=? AND UID=?", (gid, uid)).fetchone()
            return 0 if r is None else r[0]
        except:
            raise Exception('查找皇后发生错误')    



# 记录决斗和下注数据


class DuelJudger:
    def __init__(self):
        self.on = {}
        self.accept_on = {}
        self.support_on = {}
        self.fire_on = {}
        self.deadnum = {}
        self.support = {}
        self.turn = {}
        self.duelid = {}
        self.isaccept = {}
        self.hasfired_on = {}

    def set_support(self, gid):
        self.support[gid] = {}

    def get_support(self, gid):
        return self.support[gid] if self.support.get(gid) is not None else 0

    def add_support(self, gid, uid, id, score):
        self.support[gid][uid] = [id, score]

    def get_support_id(self, gid, uid):
        if self.support[gid].get(uid) is not None:
            return self.support[gid][uid][0]
        else:
            return 0

    def get_support_score(self, gid, uid):
        if self.support[gid].get(uid) is not None:
            return self.support[gid][uid][1]
        else:
            return 0

    # 五个开关：决斗，接受，下注， 开枪, 是否已经开枪

    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def turn_on(self, gid):
        self.on[gid] = True

    def turn_off(self, gid):
        self.on[gid] = False

    def get_on_off_accept_status(self, gid):
        return self.accept_on[gid] if self.accept_on.get(gid) is not None else False

    def turn_on_accept(self, gid):
        self.accept_on[gid] = True

    def turn_off_accept(self, gid):
        self.accept_on[gid] = False

    def get_on_off_support_status(self, gid):
        return self.support_on[gid] if self.support_on.get(gid) is not None else False

    def turn_on_support(self, gid):
        self.support_on[gid] = True

    def turn_off_support(self, gid):
        self.support_on[gid] = False

    def get_on_off_fire_status(self, gid):
        return self.fire_on[gid] if self.fire_on.get(gid) is not None else False

    def turn_on_fire(self, gid):
        self.fire_on[gid] = True

    def turn_off_fire(self, gid):
        self.fire_on[gid] = False

    def get_on_off_hasfired_status(self, gid):
        return self.hasfired_on[gid] if self.hasfired_on.get(gid) is not None else False

    def turn_on_hasfired(self, gid):
        self.hasfired_on[gid] = True

    def turn_off_hasfired(self, gid):
        self.hasfired_on[gid] = False

    # 记录决斗者id
    def init_duelid(self, gid):
        self.duelid[gid] = []

    def set_duelid(self, gid, id1, id2):
        self.duelid[gid] = [id1, id2]

    def get_duelid(self, gid):
        return self.duelid[gid] if self.accept_on.get(gid) is not None else [0, 0]
        
    # 查询一个决斗者是1号还是2号
    def get_duelnum(self, gid, uid):
        return self.duelid[gid].index(uid) + 1

    # 记录由谁开枪
    def init_turn(self, gid):
        self.turn[gid] = 1

    def get_turn(self, gid):
        return self.turn[gid] if self.turn[gid] is not None else 0

    def change_turn(self, gid):
        if self.get_turn(gid) == 1:
            self.turn[gid] = 2
            return 2
        else:
            self.turn[gid] = 1
            return 1

    # 记录子弹位置
    def init_deadnum(self, gid):
        self.deadnum[gid] = None

    def set_deadnum(self, gid, num):
        self.deadnum[gid] = num

    def get_deadnum(self, gid):
        return self.deadnum[gid] if self.deadnum[gid] is not None else False

    # 记录是否接受
    def init_isaccept(self, gid):
        self.isaccept[gid] = False

    def on_isaccept(self, gid):
        self.isaccept[gid] = True

    def off_isaccept(self, gid):
        self.isaccept[gid] = False

    def get_isaccept(self, gid):
        return self.isaccept[gid] if self.isaccept[gid] is not None else False


duel_judger = DuelJudger()


# 随机生成一个pcr角色id，应该已经被替代了
def get_pcr_id():
    chara_id_list = list(_pcr_data.CHARA_NAME.keys())
    while True:
        random.shuffle(chara_id_list)
        if chara_id_list[0] not in BLACKLIST_ID: break
    return chara_id_list[0]


# 生成没被约过的角色列表
def get_newgirl_list(gid):
    chara_id_list = list(_pcr_data.CHARA_NAME.keys())
    duel = DuelCounter()
    old_list = duel._get_card_list(gid)
    dlc_blacklist = get_dlc_blacklist(gid)
    new_list = []
    for card in chara_id_list:
        if card not in BLACKLIST_ID and card not in old_list and card not in dlc_blacklist:
            new_list.append(card)
    return new_list


# 取爵位名
def get_noblename(level: int):
    namedict = {
        "1": "男爵",
        "2": "子爵",
        "3": "伯爵",
        "4": "侯爵",
        "5": "公爵",
        "6": "国王",
        "7": "皇帝"
    }
    return namedict[str(level)]


# 返回爵位对应的女友数
def get_girlnum(level: int):
    numdict = LEVEL_GIRL_NEED
    return numdict[str(level)]


# 返回升级到爵位所需要的金币数
def get_noblescore(level: int):
    numdict = LEVEL_COST_DICT
    return numdict[str(level)]

# 判断当前女友数是否大于于爵位上限
def girl_outlimit(gid,uid):
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    girlnum = get_girlnum(level)
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist) 
    if cidnum > girlnum:
        return True
    else: 
        return False
        

        
#魔改图片拼接 
def concat_pic(pics, border=0):
    num = len(pics)
    w= pics[0].size[0]
    h_sum = 0
    for pic in pics:
        h_sum += pic.size[1]
    des = Image.new('RGBA', (w, h_sum + (num-1) * border), (255, 255, 255, 255))
    h = 0
    for i, pic in enumerate(pics):
        des.paste(pic, (0, (h + i*border)), pic)
        h += pic.size[1]        
    return des


@sv.on_fullmatch(['本群贵族状态','查询本群贵族','本群贵族'])
async def group_noble_status(bot, ev: CQEvent):
    gid = ev.group_id
    duel = DuelCounter()
    newgirllist = get_newgirl_list(gid)
    newgirlnum = len(newgirllist)
    l1_num = duel._get_level_num(gid,1)
    l2_num = duel._get_level_num(gid,2)
    l3_num = duel._get_level_num(gid,3)
    l4_num = duel._get_level_num(gid,4)
    l5_num = duel._get_level_num(gid,5)
    l6_num = duel._get_level_num(gid,6)
    l7_num = duel._get_level_num(gid,7)
    dlctext=''
    for dlc in dlcdict.keys():
        if gid in dlc_switch[dlc]:
            dlctext += f'{dlc},'
    msg=f'''
╔                          ╗
         本群贵族
      
  皇帝：{l7_num}名
  国王：{l6_num}名
  公爵：{l5_num}名
  侯爵：{l4_num}名
  伯爵：{l3_num}名
  子爵：{l2_num}名
  男爵：{l1_num}名
  已开启DLC:
  {dlctext}
  还有{newgirlnum}名单身女友 
╚                          ╝
'''
    await bot.send(ev, msg)


@sv.on_fullmatch('贵族签到')
async def noblelogin(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    guid = gid, uid
    if not daily_sign_limiter.check(guid):
        await bot.send(ev, '今天已经签到过了哦，明天再来吧', at_sender=True)
        return
    duel = DuelCounter()
    
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅'
        await bot.send(ev, msg, at_sender=True)
        return
    #根据概率随机获得收益 
    score_counter = ScoreCounter2()
    daily_sign_limiter.increase(guid)    
    loginnum_ = ['1','2', '3', '4']  
    r_ = [0.3, 0.4, 0.2, 0.1]  
    sum_ = 0
    ran = random.random()
    for num, r in zip(loginnum_, r_):
        sum_ += r
        if ran < sum_ :break
    Bonus = {'1':[100,Login100],
             '2':[200,Login200],
             '3':[300,Login300],    
             '4':[600,Login600]
            }             
    score1 = Bonus[num][0]
    text1 = random.choice(Bonus[num][1])
    
    #根据爵位的每日固定收入
    level = duel._get_level(gid, uid)
    score2 = 10*(10**level)
    noblename = get_noblename(level)
    score = score_counter._get_score(gid, uid)
    msg = f'\n{text1}\n签到成功！您领取了：\n\n{score1}金币(随机)和\n{score2}金币({noblename}爵位)'
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)
    #女友工作收入
    score3 = 1500*cidnum
    scoresum = score1+score2+score3
    score_counter._add_score(gid, uid, scoresum)
    
    msg +=f'\n今日女友们的收入是{score3}金币\n你总共获取{scoresum}金币'

    
    await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch('创建贵族')
async def add_noble(bot, ev: CQEvent):
    try:
        gid = ev.group_id
        uid = ev.user_id
        duel = DuelCounter()
        if duel._get_level(gid, uid) != 0:
            msg = '您已经在本群创建过贵族了，请发送 查询贵族 查询'
            await bot.send(ev, msg, at_sender=True)
            return
        
        #判定本群女友是否已空，如果空则分配一个复制人可可萝
        newgirllist = get_newgirl_list(gid)
        if len(newgirllist) == 0:
            cid = 9999
            c = chara.fromid(1059)
            girlmsg = f'本群已经没有可以约的女友了哦，一位神秘的可可萝在你孤单时来到了你身边。{c.icon.cqcode}'
        else:
            cid = random.choice(newgirllist)
            c = chara.fromid(cid)
            girlmsg = f'为您分配的初始女友为：{c.name}{c.icon.cqcode}'
        duel._add_card(gid, uid, cid)
        duel._set_level(gid, uid, 1)
        score_counter = ScoreCounter2()
        roll = random.randint(1,10000)
        if roll <= 1000:
            get_score = random.randint(1,5)
            score_counter._add_score(gid, uid, get_score)
            famliy = '饥寒交迫'
        elif 1000 < roll <=3000:
            get_score = random.randint(5,50)
            score_counter._add_score(gid, uid, get_score)
            famliy = '豕食丐衣'
        elif 3000 < roll <=7000:
            get_score = random.randint(50,500)
            score_counter._add_score(gid, uid, get_score)
            famliy = '桑户蓬枢'
        elif 7000 < roll <=9000:
            get_score = random.randint(500,5000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '家道小康 '
        elif 9000 < roll <=9500:
            get_score = random.randint(5000,10000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '丰衣足食'
        elif 9500 < roll <=9700:
            get_score = random.randint(10000,20000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '乘坚策肥'
        elif 9700 < roll <=9900:
            get_score = random.randint(20000,50000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '家财万贯'
        elif 9900 < roll <=9999:
            get_score = random.randint(50000,100000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '阶级敌人'
        else:
            get_score = random.randint(100000,500000)
            score_counter._add_score(gid, uid, get_score)
            famliy = '富可敌国'
        msg = f'\n创建贵族成功！\n您的初始爵位是男爵\n你的家境为{famliy}\n你的启动资金为{get_score}金币\n{girlmsg}'
        await bot.send(ev, msg, at_sender=True)        
            

    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_fullmatch(['查询贵族', '贵族查询', '我的贵族'])
async def inquire_noble(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅'
        await bot.send(ev, msg, at_sender=True)
        return
    level = duel._get_level(gid, uid)
    noblename = get_noblename(level)
    girlnum = get_girlnum(level)
    score = score_counter._get_score(gid, uid)
    charalist = []

    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)
    if cidnum == 0:
        msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  您共可拥有{girlnum}名女友
  您目前没有女友
  发送[贵族约会]
  可以招募女友哦
  
╚                          ╝
'''
        await bot.send(ev, msg, at_sender=True)

    else:
        for cid in cidlist:
            #替换复制人可可萝
            if cid == 9999:
                cid = 1059
            charalist.append(chara.Chara(cid, 0, 0))
            
            
        #制图部分，六个一行
        num = copy.deepcopy(cidnum)
        position = 6
        if num <= 6:
            res = chara.gen_team_pic(charalist, star_slot_verbose=False)
        else:
            num -= 6
            res = chara.gen_team_pic(charalist[0:position], star_slot_verbose=False)
            while(num > 0):
                if num>=6:
                    res1 = chara.gen_team_pic(charalist[position:position+6], star_slot_verbose=False)
                else: 
                    res1 = chara.gen_team_pic(charalist[position:], star_slot_verbose=False)
                res = concat_pic([res, res1])
                position +=6
                num -= 6
            

        bio = BytesIO()
        res.save(bio, format='PNG')
        base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
        mes = f"[CQ:image,file={base64_str}]"
        
        #判断是否开启声望
        prestige = score_counter._get_prestige(gid,uid)
        if prestige == None:
            partmsg = '未开启声望系统'
        else:
            partmsg = f'您的声望为{prestige}点'
        
        
        
        
        
        msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  {partmsg}
  您共可拥有{girlnum}名女友
  您已拥有{cidnum}名女友
  她们是：
    {mes}   
╚                          ╝
'''
        #判断有无皇后
        queen = duel._search_queen(gid,uid)
        if queen != 0:
            c = chara.fromid(queen)
            
            msg = f'''
╔                          ╗
  您的爵位为{noblename}
  您的金币为{score}
  {partmsg}
  您的皇后是{c.name}
  您共可拥有{girlnum}名女友
  您已拥有{cidnum}名女友
  她们是：
    {mes}  
    
╚                          ╝
'''


        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['招募女友', '贵族舞会', '贵族约会'])
async def add_girl(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel_judger.get_on_off_accept_status(gid):
        msg = '现在正在决斗中哦，请决斗后再参加舞会吧'
        await bot.send(ev, msg, at_sender=True)
        return        

    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅'
        duel_judger.turn_off(ev.group_id)

        await bot.send(ev, msg, at_sender=True)
        return
    else:
        # 防止女友数超过上限
        level = duel._get_level(gid, uid)
        noblename = get_noblename(level)
        girlnum = get_girlnum(level)
        cidlist = duel._get_cards(gid, uid)
        cidnum = len(cidlist)
        if cidnum >= girlnum:
            msg = '您的女友已经满了哦，快点发送[升级贵族]进行升级吧'
            await bot.send(ev, msg, at_sender=True)
            return
        if cidnum == 0:
            new_COST = GACHA_COST
        else:
            new_COST = GACHA_COST*cidnum*level
        score = score_counter._get_score(gid, uid)
        if score < new_COST:
            msg = f'您的金币不足{new_COST}哦'
            await bot.send(ev, msg, at_sender=True)
            return
        newgirllist = get_newgirl_list(gid)
        # 判断女友是否被抢没和该用户是否已经没有女友
        if len(newgirllist) == 0:
            if cidnum!=0:
                await bot.send(ev, '这个群已经没有可以约到的新女友了哦', at_sender=True)
                return        
            else : 
                score_counter._reduce_score(gid, uid, GACHA_COST)
                cid = 9999
                c = chara.fromid(1059)
                duel._add_card(gid, uid, cid)
                msg = f'本群已经没有可以约的女友了哦，一位神秘的可可萝在你孤单时来到了你身边{c.icon.cqcode}'
                await bot.send(ev, msg, at_sender=True)
                return

        score_counter._reduce_score(gid, uid, new_COST)

        # 招募女友失败
        if random.random() < 0.5:
            losetext = random.choice(Addgirlfail)
            msg = f'\n{losetext}\n您花费了{new_COST}金币，但是没有约到新的女友'
            await bot.send(ev, msg, at_sender=True)
            return

        # 招募女友成功
        cid = random.choice(newgirllist)

        duel._add_card(gid, uid, cid)
        c = chara.fromid(cid)
        wintext = random.choice(Addgirlsuccess)
        mes = c.icon.cqcode
        PIC_PATH = os.path.join(FILE_PATH,'fullcard')
        path = os.path.join(PIC_PATH,f'{cid}31.png')
        if  os.path.exists(path):
            img = Image.open(path)
            bio = BytesIO()
            img.save(bio, format='PNG')
            base64_str = 'base64://' + base64.b64encode(bio.getvalue()).decode()
            mes = f"[CQ:image,file={base64_str}]"


        msg = f'\n{wintext}\n招募女友成功！\n您花费了{GACHA_COST}金币\n新招募的女友为：{c.name}{mes}'

        await bot.send(ev, msg, at_sender=True)


@sv.on_fullmatch(['升级爵位', '升级贵族','贵族升级'])
async def add_girl(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    score = score_counter._get_score(gid, uid)
    level = duel._get_level(gid, uid)
    noblename = get_noblename(level)
    girlnum = get_girlnum(level)
    cidlist = duel._get_cards(gid, uid)
    cidnum = len(cidlist)

    if duel_judger.get_on_off_accept_status(gid):
        msg = '现在正在决斗中哦，请决斗后再升级爵位吧'
        await bot.send(ev, msg, at_sender=True)
        return  
    if duel._get_level(gid, uid) == 0:
        msg = '您还未在本群创建过贵族，请发送 创建贵族 开始您的贵族之旅'
        await bot.send(ev, msg, at_sender=True)
        return

    if level == 6:
        msg = f'您已经是国王了， 需要通过声望加冕称帝哦'
        await bot.send(ev, msg, at_sender=True)
        return

    if level == 7:
        msg = f'您是本群的皇帝， 已经无法提升等级了'
        await bot.send(ev, msg, at_sender=True)
        return


    if cidnum < girlnum:
        msg = f'您的女友没满哦\n需要达到{girlnum}名女友\n您现在有{cidnum}名'
        await bot.send(ev, msg, at_sender=True)
        return
    needscore = get_noblescore(level + 1)
    futurename = get_noblename(level + 1)

    if score < needscore:
        msg = f'您的金币不足哦\n升级到{futurename}需要{needscore}金币'
        await bot.send(ev, msg, at_sender=True)
        return
    score_counter._reduce_score(gid, uid, needscore)
    duel._add_level(gid, uid)
    newlevel = duel._get_level(gid, uid)
    newnoblename = get_noblename(newlevel)
    newgirlnum = get_girlnum(newlevel)
    msg = f'花费了{needscore}金币\n您成功由{noblename}升到了{newnoblename}\n可以拥有{newgirlnum}名女友了哦'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix('贵族决斗')
async def nobleduel(bot, ev: CQEvent):
    if ev.message[0].type == 'at':
        id2 = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    if duel_judger.get_on_off_status(ev.group_id):
        await bot.send(ev, "此轮决斗还没结束，请勿重复使用指令")
        return
        
    gid = ev.group_id
    duel_judger.turn_on(gid)
    id1 = ev.user_id
    duel = DuelCounter()
    is_overtime = 0
    if id2 == id1:
        await bot.send(ev, "不能和自己决斗！", at_sender=True)
        duel_judger.turn_off(ev.group_id)
        return 

    if duel._get_level(gid, id1) == 0:
        msg = f'[CQ:at,qq={id1}]决斗发起者还未在创建过贵族\n请发送 创建贵族 开始您的贵族之旅'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id1) == {}:
        msg = f'[CQ:at,qq={id1}]您没有女友，不能参与决斗哦'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return

    if duel._get_level(gid, id2) == 0:
        msg = f'[CQ:at,qq={id2}]被决斗者还未在本群创建过贵族\n请发送 创建贵族 开始您的贵族之旅'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    if duel._get_cards(gid, id2) == {}:
        msg = f'[CQ:at,qq={id2}]您没有女友，不能参与决斗哦'
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    #判定每日上限
    guid = gid ,id1
    if not daily_duel_limiter.check(guid):
        await bot.send(ev, '今天的决斗次数已经超过上限了哦，明天再来吧', at_sender=True)
        duel_judger.turn_off(ev.group_id)
        return
    daily_duel_limiter.increase(guid)



    # 判定双方的女友是否已经超过上限

    # 这里设定大于才会提醒，就是可以超上限1名，可以自己改成大于等于
    if girl_outlimit(gid,id1):
        msg = f'[CQ:at,qq={id1}]您的女友超过了爵位上限，本次决斗获胜只能获得金币哦'
        await bot.send(ev, msg)
    if girl_outlimit(gid,id2):
        msg = f'[CQ:at,qq={id2}]您的女友超过了爵位上限，本次决斗获胜只能获得金币哦'
        await bot.send(ev, msg)
    duel_judger.init_isaccept(gid)
    duel_judger.set_duelid(gid, id1, id2)
    duel_judger.turn_on_accept(gid)
    msg = f'[CQ:at,qq={id2}]对方向您发起了优雅的贵族决斗，请在{WAIT_TIME}秒内[接受/拒绝]'

    await bot.send(ev, msg)
    await asyncio.sleep(WAIT_TIME)
    duel_judger.turn_off_accept(gid)
    if duel_judger.get_isaccept(gid) is False:
        msg = '决斗被拒绝'
        duel_judger.turn_off(gid)
        await bot.send(ev, msg, at_sender=True)
        return
    duel = DuelCounter()
    level1 = duel._get_level(gid, id1)
    noblename1 = get_noblename(level1)
    level2 = duel._get_level(gid, id2)
    noblename2 = get_noblename(level2)
    msg = f'''对方接受了决斗！    
1号：[CQ:at,qq={id1}]
爵位为：{noblename1}
2号：[CQ:at,qq={id2}]
爵位为：{noblename2}
其他人请在{DUEL_SUPPORT_TIME}秒选择支持的对象
[支持1/2号xxx金币]'''

    await bot.send(ev, msg)
    duel_judger.turn_on_support(gid)
    await asyncio.sleep(DUEL_SUPPORT_TIME)
    duel_judger.turn_off_support(gid)
    deadnum = random.randint(1, 6)
    duel_judger.set_deadnum(gid, deadnum)
    duel_judger.init_turn(gid)
    duel_judger.turn_on_fire(gid)
    duel_judger.turn_off_hasfired(gid)
    msg = f'支持环节结束，下面请决斗双方轮流[开枪]\n[CQ:at,qq={id1}]先开枪，30秒未开枪自动认输'

    await bot.send(ev, msg)
    n = 1
    while (n <= 6):
        wait_n = 0
        while (wait_n < 30):
            if duel_judger.get_on_off_hasfired_status(gid):
                break

            wait_n += 1
            await asyncio.sleep(1)
        if wait_n >= 30:
            # 超时未开枪的胜负判定
            loser = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
            winner = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
            msg = f'[CQ:at,qq={loser}]\n你明智的选择了认输'
            await bot.send(ev, msg)
            
            #记录本局为超时局
            is_overtime = 1
            
            
            break
        else:
            if n == duel_judger.get_deadnum(gid):
                # 被子弹打到的胜负判定
                loser = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
                winner = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
                msg = f'[CQ:at,qq={loser}]\n砰！你死了'
                await bot.send(ev, msg)
                break
            else:
                id = duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]
                id2 = duel_judger.get_duelid(gid)[2 - duel_judger.get_turn(gid)]
                msg = f'[CQ:at,qq={id}]\n砰！松了一口气，你并没有死\n[CQ:at,qq={id2}]\n轮到你开枪了哦'
                await bot.send(ev, msg)
                n += 1
                duel_judger.change_turn(gid)
                duel_judger.turn_off_hasfired(gid)
                duel_judger.turn_on_fire(gid)
    score_counter = ScoreCounter2()
    cidlist = duel._get_cards(gid, loser)
    selected_girl = random.choice(cidlist)
    queen = duel._search_queen(gid,loser)

    #判定被输掉的是否是复制人可可萝，是则换成金币
    if selected_girl==9999:
        score_counter._add_score(gid, winner, 3000)
        c = chara.fromid(1059)
        duel._delete_card(gid, loser, selected_girl)
        msg = f'[CQ:at,qq={winner}]\n您赢得了神秘的可可萝，但是她微笑着消失了\n本次决斗获得了3000金币'
        await bot.send(ev, msg)
        msg = f'[CQ:at,qq={loser}]\n您输掉了贵族决斗，被抢走了女友\n{c.name}，\n只要招募，她就还会来到你的身边哦{c.icon.cqcode}'
        await bot.send(ev, msg)

    #判断被输掉的是否为皇后    
    elif selected_girl==queen:
        level = duel._get_level(gid, winner)
        win_score = 3000*level+10**level
        score_counter._add_score(gid, winner, win_score)
        msg = f'[CQ:at,qq={winner}]您赢得的角色为对方的皇后，\n您改为获得{win_score}金币'
        await bot.send(ev, msg)
        score_counter._reduce_prestige(gid,loser,500)
        msg = f'[CQ:at,qq={loser}]您差点输掉了皇后，失去了500声望'
        await bot.send(ev, msg)


    elif girl_outlimit(gid,winner):
        level = duel._get_level(gid, winner)
        win_score = 3000*level+10**(level+1)
        score_counter._add_score(gid, winner, win_score)
        c = chara.fromid(selected_girl)
        duel._delete_card(gid, loser, selected_girl)
        msg = f'[CQ:at,qq={winner}]您的女友超过了爵位上限,本次决斗获得了{win_score}金币\n[CQ:at,qq={loser}]您输掉了贵族决斗且对方超过了爵位上限，您的女友恢复了单身\n{c.name}{c.icon.cqcode}'
        await bot.send(ev, msg)

    else:
        c = chara.fromid(selected_girl)
        duel._delete_card(gid, loser, selected_girl)
        duel._add_card(gid, winner, selected_girl)
        msg = f'[CQ:at,qq={loser}]您输掉了贵族决斗，您被抢走了女友\n{c.name}{c.icon.cqcode}'
        await bot.send(ev, msg)
        #判断赢家的角色列表里是否有复制人可可萝
        wincidlist = duel._get_cards(gid, winner)
        if 9999 in wincidlist:
            duel._delete_card(gid, winner, 9999)
            score_counter._add_score(gid, winner, 300)
            msg = f'[CQ:at,qq={winner}]\n“主人有了女友已经不再孤单了，我暂时离开了哦”\n您赢得了{c.name},可可萝微笑着消失了\n您获得了300金币'
            await bot.send(ev, msg)
    #判断胜者败者是否需要增减声望
    winprestige = score_counter._get_prestige(gid,winner)
    if winprestige != None:
        score_counter._add_prestige(gid,winner,200)
        msg = f'[CQ:at,qq={winner}]决斗胜利使您的声望上升了200点'
        await bot.send(ev, msg)
    loseprestige = score_counter._get_prestige(gid,loser)
    if loseprestige != None:
        score_counter._reduce_prestige(gid,loser,100)
        msg = f'[CQ:at,qq={loser}]决斗失败使您的声望下降了100点'
        await bot.send(ev, msg)


    #判定败者是否掉爵位，皇帝不会因为决斗掉爵位
    level_loser = duel._get_level(gid, loser)
    if level_loser > 1 and level_loser!=7:
        noblename_loser = get_noblename(level_loser)
        girlnum_loser = get_girlnum(level_loser - 1)
        cidlist_loser = duel._get_cards(gid, loser)
        cidnum_loser = len(cidlist_loser)
        if cidnum_loser < girlnum_loser:
            duel._reduce_level(gid, loser)
            new_noblename = get_noblename(level_loser - 1)
            msg = f'[CQ:at,qq={loser}]\n您的女友数为{cidnum_loser}名\n小于爵位需要的女友数{girlnum_loser}名\n您的爵位下降到了{new_noblename}'
            await bot.send(ev, msg)

    #结算下注金币，判定是否为超时局
    if is_overtime == 1 and n!=6:
        msg = '本局为超时局，不进行金币结算，支持的金币全部返还'
        duel_judger.set_support(ev.group_id)
        duel_judger.turn_off(ev.group_id)
        await bot.send(ev, msg)
        return
    
    support = duel_judger.get_support(gid)
    winuid = []
    supportmsg = '金币结算:\n'
    winnum = duel_judger.get_duelnum(gid, winner)

    if support != 0:
        for uid in support:
            support_id = support[uid][0]
            support_score = support[uid][1]
            if support_id == winnum:
                winuid.append(uid)
                #这里是赢家获得的金币结算，可以自己修改倍率
                winscore = support_score*WIN_NUM 
                score_counter._add_score(gid, uid, winscore)
                supportmsg += f'[CQ:at,qq={uid}]+{winscore}金币\n'
            else:
                score_counter._reduce_score(gid, uid, support_score)
                supportmsg += f'[CQ:at,qq={uid}]-{support_score}金币\n'
    await bot.send(ev, supportmsg)
    duel_judger.set_support(ev.group_id)
    duel_judger.turn_off(ev.group_id)
    return


@sv.on_fullmatch('接受')
async def duelaccept(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_accept_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[1]:
            gid = ev.group_id
            msg = '贵族决斗接受成功，请耐心等待决斗开始'
            await bot.send(ev, msg, at_sender=True)
            duel_judger.turn_off_accept(gid)
            duel_judger.on_isaccept(gid)
        else:
            print('不是被决斗者')
    else:
        print('现在不在决斗期间')


@sv.on_fullmatch('拒绝')
async def duelrefuse(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_accept_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[1]:
            gid = ev.group_id
            msg = '您已拒绝贵族决斗'
            await bot.send(ev, msg, at_sender=True)
            duel_judger.turn_off_accept(gid)
            duel_judger.off_isaccept(gid)


@sv.on_fullmatch('开枪')
async def duelfire(bot, ev: CQEvent):
    gid = ev.group_id
    if duel_judger.get_on_off_fire_status(gid):
        if ev.user_id == duel_judger.get_duelid(gid)[duel_judger.get_turn(gid) - 1]:
            duel_judger.turn_on_hasfired(gid)
            duel_judger.turn_off_fire(gid)


@sv.on_rex(r'^支持(1|2)号(\d+)(金币|币)$')
async def on_input_duel_score(bot, ev: CQEvent):
    try:
        if duel_judger.get_on_off_support_status(ev.group_id):
            gid = ev.group_id
            uid = ev.user_id

            match = ev['match']
            select_id = int(match.group(1))
            input_score = int(match.group(2))
            print(select_id, input_score)
            score_counter = ScoreCounter2()
            # 若下注该群下注字典不存在则创建
            if duel_judger.get_support(gid) == 0:
                duel_judger.set_support(gid)
            support = duel_judger.get_support(gid)
            # 检查是否重复下注
            if uid in support:
                msg = '您已经支持过了'
                await bot.send(ev, msg, at_sender=True)
                return
            # 检查是否是决斗人员
            duellist = duel_judger.get_duelid(gid)
            if uid in duellist:
                msg = '决斗参与者不能支持'
                await bot.send(ev, msg, at_sender=True)
                return

                # 检查金币是否足够下注
            if score_counter._judge_score(gid, uid, input_score) == 0:
                msg = '您的金币不足'
                await bot.send(ev, msg, at_sender=True)
                return
            else:
                duel_judger.add_support(gid, uid, select_id, input_score)
                msg = f'支持{select_id}号成功'
                await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


# 以下部分与赛跑的重合，有一个即可，两个插件都装建议注释掉

@sv.on_fullmatch(['领金币', '领取金币'])
async def add_score(bot, ev: CQEvent):
    try:
        score_counter = ScoreCounter2()
        gid = ev.group_id
        uid = ev.user_id

        current_score = score_counter._get_score(gid, uid)
        if current_score == 0:
            score_counter._add_score(gid, uid, ZERO_GET_AMOUNT)
            msg = f'您已领取{ZERO_GET_AMOUNT}金币'
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            msg = '金币为0才能领取哦'
            await bot.send(ev, msg, at_sender=True)
            return
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))

@sv.on_fullmatch(['贵族抽签', '贵族祈祷'])
async def chouqian_score(bot, ev: CQEvent):
    try:
        score_counter = ScoreCounter2()
        gid = ev.group_id
        uid = ev.user_id
        guid = gid, uid
        if not daily_qidao_limiter.check(guid):
            await bot.send(ev, '今日神明已不想见你，明天再来吧', at_sender=True)
            return
        current_score = score_counter._get_score(gid, uid)
        if  current_score > 100000:
            msg = f'神明不再回应深陷欲望旋涡中之人~'
            await bot.send(ev, msg, at_sender=True)
            return
        elif current_score < 100:
            msg = f'祈祷一次耗费一杯圣水(100金币),你的钱不够~'
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            score_counter._reduce_score(gid, uid,100)
            current_score = score_counter._get_score(gid, uid)
            roll = random.random()
            if roll <= 0.01:
                daily_qidao_limiter.increase(guid)
                #score_counter._reduce_score(gid, uid,current_score)
                get_score = random.randint(100000,500000)
                score_counter._add_score(gid, uid, get_score)
                msg = f'你虔诚的心感动了神明,突然仿佛听到神灵在低语,你获得了{get_score}金币'
                await bot.send(ev, msg, at_sender=True)
            elif 0.01 < roll <= 0.1:
                daily_qidao_limiter.increase(guid)
                times = random.randint(1,5)
                get_score = current_score*times
                score_counter._add_score(gid, uid, get_score)
                msg = f'你像往常一样祈祷,突然福至心灵,你的金币增加了{times}倍'
                await bot.send(ev, msg, at_sender=True)
            elif 0.1 < roll <= 0.3:
                daily_qidao_limiter.increase(guid)
                get_score = random.randint(100,5000)
                score_counter._add_score(gid, uid, get_score)
                msg = f'你低头祈祷着,突然一阵恍惚,你的金币增加了{get_score}'
                await bot.send(ev, msg, at_sender=True)
            elif 0.3 < roll <= 0.7:
                daily_qidao_limiter.increase(guid)
                msg = f'你平静地祈祷着,感觉周围很安静,什么也没发生'
                await bot.send(ev, msg, at_sender=True)
            elif 0.7 < roll <= 0.9:
                daily_qidao_limiter.increase(guid)
                lose_score = random.randint(100,50000)
                if current_score < lose_score:
                    lose_score = current_score
                score_counter._reduce_score(gid, uid, lose_score)
                msg = f'你心不在焉地祈祷,突然感到心慌,你的金币被偷了{lose_score}'
                await bot.send(ev, msg, at_sender=True)
            elif 0.9 < roll < 0.98:
                daily_qidao_limiter.increase(guid)
                lose_score = current_score-1
                score_counter._reduce_score(gid, uid, lose_score)
                msg = f'你假装真诚地祈祷,突然一阵心悸,你的金币变成了沙子,只剩下你攥在掌心的那一枚'
                await bot.send(ev, msg, at_sender=True)
            else:
                daily_qidao_limiter.increase(guid)
                get_score = current_score*10
                score_counter._add_score(gid, uid, get_score)
                msg = f'你正在祈祷,突然听见神在你耳边低语:永远不要相信恶魔,你的金钱增加了10倍'
                await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_prefix(['查金币', '查询金币', '查看金币'])
async def get_score(bot, ev: CQEvent):
    try:
        score_counter = ScoreCounter2()
        gid = ev.group_id
        uid = ev.user_id

        current_score = score_counter._get_score(gid, uid)
        msg = f'您的金币为{current_score}'
        await bot.send(ev, msg, at_sender=True)
        return
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_prefix(('充值金币'))
async def cheat_score(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '不要想着走捷径哦', at_sender=True)
    gid = ev.group_id
    uid = ev.user_id
    sid = None
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    duel = DuelCounter()
    score_counter = ScoreCounter2()
    if duel._get_level(gid, sid) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦', at_sender=True)
    score_counter._add_score(gid, sid, num)
    score = score_counter._get_score(gid, sid)
    msg = f'已为[CQ:at,qq={sid}]充值{num}金币\n现在共有{score}金币'
    await bot.send(ev, msg)


@sv.on_fullmatch('重置决斗')
async def init_duel(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能使用重置决斗哦', at_sender=True)
    duel_judger.turn_off(ev.group_id)
    msg = '已重置本群决斗状态！'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['查女友', '查询女友', '查看女友'])
async def search_girl(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    if not args:
        await bot.send(ev, '请输入查女友+pcr角色名', at_sender=True)
        return
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.send(ev, '请输入正确的pcr角色名', at_sender=True)
        return
    duel = DuelCounter()
    owner = duel._get_card_owner(gid, cid)
    c = chara.fromid(cid)
    #判断是否是皇后
    print(duel._get_queen_owner(gid,cid))
    if duel._get_queen_owner(gid,cid) !=0 :
        owner = duel._get_queen_owner(gid,cid)
        await bot.finish(ev, f'\n{c.name}现在是\n[CQ:at,qq={owner}]的皇后哦{c.icon.cqcode}', at_sender=True)

    if owner == 0:
        await bot.send(ev, f'{c.name}现在还是单身哦，快去约到她吧', at_sender=True)
        return
    else:
        msg = f'{c.name}现在正在\n[CQ:at,qq={owner}]的身边哦{c.icon.cqcode}'
        await bot.send(ev, msg)


#重置某一用户的金币，只用做必要时删库用
@sv.on_prefix('重置金币')
async def reset_score(bot, ev: CQEvent):
    gid = ev.group_id
    sid = None
    uid = ev.user_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    duel = DuelCounter()
    if duel._get_level(gid, sid) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦', at_sender=True)
    if uid == sid or priv.check_priv(ev,priv.OWNER):
        score_counter = ScoreCounter2()    
        current_score = score_counter._get_score(gid, sid)
        score_counter._reduce_score(gid, sid,current_score)
        await bot.finish(ev, f'已清空[CQ:at,qq={sid}]的金币', at_sender=True)
    else:
        await bot.send(ev, '只有群主才重置别人的金币哦~', at_sender=True)
        
#注意会清空此人的角色以及贵族等级，只用做必要时删库用 
@sv.on_prefix(['重置角色','贵族转生','贵族重生'])
async def reset_chara(bot, ev: CQEvent):
    gid = ev.group_id
    sid = None
    uid = ev.user_id
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            sid = int(m.data['qq'])
        elif m.type == 'at' and m.data['qq'] == 'all':
            await bot.send(ev, '人干事？', at_sender=True)
            return
    if sid is None:
        sid = uid
    guid = gid, sid
    if not daily_chongsheng_limiter.check(guid):
            await bot.send(ev, '今日冥王不想见你,你无法继续转生', at_sender=True)
            return
    duel = DuelCounter()
    if duel._get_level(gid, sid) == 0:
        await bot.finish(ev, '该用户还未在本群创建贵族哦', at_sender=True)
    if uid == sid or priv.check_priv(ev,priv.OWNER):
        cidlist = duel._get_cards(gid, sid)
        for cid in cidlist:
            duel._delete_card(gid, sid, cid)       
        daily_chongsheng_limiter.increase(guid)
        queen = duel._search_queen(gid,sid)
        duel._delete_queen_owner(gid,queen)
        duel._set_level(gid, sid, 0)
        score_counter = ScoreCounter2()    
        current_score = score_counter._get_score(gid, sid)
        score_counter._reduce_score(gid, sid,current_score)    
        await bot.finish(ev, f'已清空[CQ:at,qq={sid}]的女友和贵族等级和金币', at_sender=True)
    else:
        await bot.send(ev, '只有群主才能重置别人的角色哦~', at_sender=True)


@sv.on_prefix('分手')
async def breakup(bot, ev: CQEvent):
    if BREAK_UP_SWITCH == True:
        gid = ev.group_id
        uid = ev.user_id    
        if duel_judger.get_on_off_accept_status(gid):
            msg = '现在正在决斗中哦，请决斗后再来谈分手事宜吧。'
            await bot.finish(ev, msg, at_sender=True)
        args = ev.message.extract_plain_text().split()
        duel = DuelCounter()
        level = duel._get_level(gid, uid)
        if level == 0:
            await bot.finish(ev, '该用户还未在本群创建贵族哦', at_sender=True)
        if not args:
            await bot.finish(ev, '请输入分手+pcr角色名', at_sender=True)
        name = args[0]
        cid = chara.name2id(name)
        if cid == 1000:
            await bot.finish(ev, '请输入正确的pcr角色名', at_sender=True)
        score_counter = ScoreCounter2()
        needscore = 3000+10**level
        score = score_counter._get_score(gid, uid)
        cidlist = duel._get_cards(gid, uid)
        if cid not in cidlist:
            await bot.finish(ev, '该角色不在你的身边哦', at_sender=True)
        #检测是否是皇后
        queen = duel._search_queen(gid,uid)
        if cid==queen:
            await bot.finish(ev, '不可以和您的皇后分手哦', at_sender=True)
        if score < needscore:
            msg = f'您的爵位分手一位女友需要{needscore}金币\n分手不易，做好准备再来吧'
            await bot.finish(ev, msg, at_sender=True)
        score_counter._reduce_score(gid, uid, needscore)
        duel._delete_card(gid, uid, cid)
        c = chara.fromid(cid)
        msg = f'\n“真正离开的那次，关门声最小”\n你和{c.name}分手了失去了{needscore}金币分手费\n{c.icon.cqcode}'
        await bot.send(ev, msg, at_sender=True)
     
@sv.on_prefix('卖女友')
async def sellma(bot, ev: CQEvent):
    if SELLMA == True:
        gid = ev.group_id
        uid = ev.user_id    
        if duel_judger.get_on_off_accept_status(gid):
            msg = '现在正在决斗中哦，请决斗后再来与恶魔做交易吧。'
            await bot.finish(ev, msg, at_sender=True)
        args = ev.message.extract_plain_text().split()
        duel = DuelCounter()
        level = duel._get_level(gid, uid)
        if level == 0:
            await bot.finish(ev, '该用户还未在本群创建贵族哦', at_sender=True)
        if not args:
            await bot.finish(ev, '请输入卖女友+pcr角色名', at_sender=True)
        name = args[0]
        cid = chara.name2id(name)
        if cid == 1000:
            await bot.finish(ev, '请输入正确的pcr角色名', at_sender=True)
        score_counter = ScoreCounter2()
        score = score_counter._get_score(gid, uid)
        cidlist = duel._get_cards(gid, uid)
        if cid not in cidlist:
            await bot.finish(ev, '该角色不在你的身边哦', at_sender=True)
        #检测是否是皇后
        queen = duel._search_queen(gid,uid)
        if cid==queen:
            score_counter._set_prestige(gid,uid,0)
            score_counter._reduce_score(gid,uid,score)
            duel._delete_queen_owner(gid,queen)
            c = chara.fromid(cid)
            msg = f'\n你将皇后{c.name}的灵魂献祭给恶魔来换取金币\n全国震怒,你的[声望]降至冰点,你的财富被用来平定叛乱,你和失去记忆的{c.name}分开\n{c.icon.cqcode}'
            await bot.finish(ev, msg, at_sender=True)
        num = 3000*level*2+12**level
        score_counter._add_score(gid, uid, num)
        duel._delete_card(gid, uid, cid)
        c = chara.fromid(cid)
        msg = f'\n你向恶魔许愿,以你和{c.name}之间的回忆为代价来换取金币.\n你和{c.name}分手得到了{num}报酬\n{c.icon.cqcode}'
        await bot.send(ev, msg, at_sender=True)

#国王以上声望部分
@sv.on_prefix(('金币兑换声望'))
async def jinbi_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    score = score_counter._get_score(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    need_score = num*10000
    if score < need_score:
        msg = f'兑换一点声望需要一万金币,你只有{score}金币' 
        await bot.send(ev, msg)
        return
    else: 
        score_counter._add_prestige(gid,uid,num)
        score_counter._reduce_score(gid,uid,need_score)
        msg = f'[CQ:at,qq={uid}]通过恶魔的契约兑换了{num}声望'
        await bot.send(ev, msg)
        

@sv.on_prefix(('声望兑换金币'))
async def shenwang_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    score = score_counter._get_score(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    get_score = num*1000
    if prestige < num:
        msg = f'一点声望可兑换一千金币,你现在有{prestige}声望' 
        await bot.send(ev, msg)
        return
    else:
        score_counter._reduce_prestige(gid,uid,num)
        score_counter._add_score(gid,uid,get_score)
        msg = f'[CQ:at,qq={uid}]通过恶魔的契约兑换了{get_score}金币'
        await bot.send(ev, msg)

@sv.on_prefix(('宝石兑换声望'))
async def baoshi_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    score = score_counter._get_score(gid, uid)
    jewel_counter = jewel.jewelCounter()
    jewel_now = jewel_counter._get_jewel(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    get_prestige = num
    if jewel_now < num:
        msg = f'宝石与声望汇率1:1,你现在有{jewel_now}宝石' 
        await bot.send(ev, msg)
        return
    else:
        jewel_counter._reduce_jewel(gid,uid,num)
        score_counter._add_prestige(gid,uid,get_prestige)
        msg = f'[CQ:at,qq={uid}]通过宝石兑换了{get_prestige}声望'
        await bot.send(ev, msg)
        
@sv.on_prefix(('声望兑换宝石'))
async def baoshi1_score(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    score = score_counter._get_score(gid, uid)
    jewel_counter = jewel.jewelCounter()
    jewel_now = jewel_counter._get_jewel(gid, uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    num = ev.message.extract_plain_text().strip()
    if not num.isdigit() and '*' not in num:
        await bot.send(ev, '数量？？？')
        return
    num = eval(num)
    get_jewel = num
    if prestige < num:
        msg = f'宝石与声望汇率1:1,你现在有{prestige}声望' 
        await bot.send(ev, msg)
        return
    else:
        score_counter._reduce_prestige(gid,uid,num)
        jewel_counter._add_jewel(gid,uid,get_jewel)
        msg = f'[CQ:at,qq={uid}]通过声望兑换了{get_jewel}宝石'
        await bot.send(ev, msg)

@sv.on_fullmatch('开启声望系统')
async def open_prestige(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    if prestige == None :
        if level < 3:
            await bot.finish(ev, '伯爵以上的地位才可以开启声望系统哦', at_sender=True)    
        else:
            score_counter._set_prestige(gid,uid,0)
            msg = '成功开启声望系统！殿下，向着更远的目标进发吧'
            await bot.send(ev, msg, at_sender=True)
    else:
        msg = '你已经开启过声望系统,请不要再开启'
        await bot.send(ev, msg, at_sender=True)
        


    
@sv.on_fullmatch('声望系统帮助')
async def prestige_help(bot, ev: CQEvent):
    msg='''
成为伯爵后才可以开启声望系统
开启后可以通过决斗等方式获取声望
声望系统相关指令如下
1. 开启声望系统
2. 查询声望
3. 加冕仪式(需要10000声望，5000金币）
4. 皇室婚礼+角色名(需3000声望，3000金币)

决斗胜利+200声望
决斗失败-100声望
皇室婚礼需皇帝才能举办
每位皇帝只能举办一次
皇后不会因决斗被抢走

 '''  
    data ={
            "type": "node",
            "data": {
                "name": '贵族小冰',
                "uin": '2854196306',
                "content": msg
            }
            }
    await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data)

@sv.on_fullmatch('查询声望')
async def inquire_prestige(bot, ev: CQEvent):
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()
    prestige = score_counter._get_prestige(gid,uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    msg = f'您的声望为{prestige}点'    
    await bot.send(ev, msg, at_sender=True)    
        
@sv.on_fullmatch(['加冕称帝','加冕仪式'])
async def be_emperor(bot, ev: CQEvent): 
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()  
    prestige = score_counter._get_prestige(gid,uid)
    
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)
    if level!=6:
        await bot.finish(ev, '只有国王才能进行加冕仪式哦。', at_sender=True)
    if prestige < 10000: 
        await bot.finish(ev, '加冕仪式需要10000声望，您的声望不足哦', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < 5000000:
        await bot.finish(ev, '加冕仪式需要5000000金币，您的金币不足哦', at_sender=True)
    score_counter._reduce_score(gid,uid,5000000)
    score_counter._reduce_prestige(gid,uid,10000)
    duel._set_level(gid, uid, 7)
    msg = '\n礼炮鸣响，教皇领唱“感恩赞美歌”“皇帝万岁！”\n在民众的欢呼声中，你加冕为了皇帝\n花费了10000点声望，5000金币'
    await bot.send(ev, msg, at_sender=True)
        
    
@sv.on_prefix('皇室婚礼')
async def marry_queen(bot, ev: CQEvent):
    args = ev.message.extract_plain_text().split()
    gid = ev.group_id
    uid = ev.user_id
    duel = DuelCounter()
    level = duel._get_level(gid, uid)
    score_counter = ScoreCounter2()  
    prestige = score_counter._get_prestige(gid,uid)
    if prestige == None:
        await bot.finish(ev, '您还未开启声望系统哦', at_sender=True)    
    if level != 7:
        await bot.finish(ev, '只有皇帝才可以举办皇室婚礼哦', at_sender=True)  
    if duel._search_queen(gid,uid)!=0:
        await bot.finish(ev, '皇帝只能有一个皇后哦', at_sender=True)
    if not args:
        await bot.finish(ev, '请输入皇室婚礼+pcr角色名', at_sender=True)
    name = args[0]
    cid = chara.name2id(name)
    if cid == 1000:
        await bot.finish(ev, '请输入正确的pcr角色名', at_sender=True)
    cidlist = duel._get_cards(gid, uid)        
    if cid not in cidlist:
        await bot.finish(ev, '该角色不在你的身边哦', at_sender=True)        
    if prestige < 30000: 
        await bot.finish(ev, '皇室婚礼需要30000声望，您的声望不足哦', at_sender=True)
    score = score_counter._get_score(gid, uid)
    if score < 30000000:
        await bot.finish(ev, '皇室婚礼需要30000000金币，您的金币不足哦', at_sender=True)    
    score_counter._reduce_prestige(gid,uid,30000)
    score_counter._reduce_score(gid,uid,30000000)    
    duel._set_queen_owner(gid,cid,uid)
    c = chara.fromid(cid)
    msg = f'繁杂的皇室礼仪过后\n\n{c.name}与[CQ:at,qq={uid}]\n\n正式踏上了婚礼的殿堂\n成为了他的皇后\n让我们为他们表示祝贺！\n皇后不会因决斗被抢走了哦\n{c.icon.cqcode}'
    await bot.send(ev, msg)
    





















    


