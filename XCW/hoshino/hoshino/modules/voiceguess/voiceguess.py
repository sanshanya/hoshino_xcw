from nonebot import MessageSegment

from hoshino import Service
from hoshino.typing import CQEvent
from hoshino.modules.priconne import chara
from bs4 import BeautifulSoup

import hoshino
import requests, os, random, asyncio


sv = Service('voiceguess', bundle='pcr娱乐', help_='''
cygames | 猜猜随机的"cygames"语音来自哪位角色
'''.strip())

DOWNLOAD_THRESHOLD = 75
MULTIPLE_VOICE_ESTERTION_ID_LIST = ['0044']
ONE_TURN_TIME = 30

class WinnerRecorder:    
    def __init__(self):
        self.on = False
        self.winner = []
        self.correct_chara_id = chara.UNKNOWN
    
    def record_winner(self, uid):
        if uid not in self.winner:
            self.winner.append(uid)
        
    def get_on_off_status(self):
        return self.on
    
    def set_correct_chara_id(self, cid):
        self.correct_chara_id = cid
    
    def turn_on(self):
        self.on = True
        
    def turn_off(self):
        self.on = False
        self.winner = []
        self.correct_chara_id = chara.UNKNOWN

     
winner_recorder = WinnerRecorder()


def download(url, file_path):
    req = requests.get(url)
    if req.status_code != 200:
        return False
    try:
        with open(file_path, 'wb') as f:
            f.write(req.content)
        return True
    except:
        return False


async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card']!='' else m['nickname']
    return d


def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]


def get_estertion_id_list():
    url = 'https://redive.estertion.win/sound/vo_ci/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    l = []
    for a in soup.find_all('a'):
        s = a['href'][:-1]
        if s.isdigit():
            l.append(s)
    return l
    
    
def estertion_id2chara_id(estertion_id):
    return (estertion_id + 1000)


@sv.on_prefix('cygames')
async def cygames_voice_guess(bot, ev: CQEvent):
    try:
        if winner_recorder.get_on_off_status():
            await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
            return
        hoshino_res_path = os.path.expanduser(hoshino.config.RES_DIR)
        dir_path = os.path.join(hoshino_res_path, 'voice_ci')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
        file_list = os.listdir(dir_path)
        if len(file_list) < DOWNLOAD_THRESHOLD:
            count = 0
            await bot.send(ev, '正在下载语音资源，请耐心等待')
            estertion_id_list = get_estertion_id_list()
            for eid in estertion_id_list:
                file_number_list = ['001'] if eid not in MULTIPLE_VOICE_ESTERTION_ID_LIST else ['001', '002']
                for file_number in file_number_list:
                    url = f'https://redive.estertion.win/sound/vo_ci/{eid}/vo_ci_1{eid[1:]}01_{file_number}.m4a'
                    file_name = url.split('/')[-1]
                    if file_name not in file_list:
                        file_path = os.path.join(dir_path, file_name)
                        if not download(url, file_path):
                            await bot.send(ev, '下载资源错误，请重试')
                            return
                        else:
                            count = count+1
            await bot.send(ev, f'下载完毕，此次下载语音包{count}个，目前共{len(os.listdir(dir_path))}个')
        
        file_list = os.listdir(dir_path)
        random.shuffle(file_list)
        if len(file_list) != 0:
            winner_recorder.turn_on()
            file_path = os.path.join(dir_path, file_list[0])
            await bot.send(ev, f'猜猜这个“cygames”语音来自哪位角色? ({ONE_TURN_TIME}s后公布答案)')
            record = MessageSegment.record(f'file:///{os.path.abspath(file_path)}')   
            await bot.send(ev, record)
            estertion_id = file_list[0][7:10]
            chara_id = estertion_id2chara_id(int(estertion_id))
            winner_recorder.set_correct_chara_id(chara_id)
            await asyncio.sleep(ONE_TURN_TIME)
            c = chara.fromid(chara_id)
            if len(winner_recorder.winner) == 0:
                msg_part = '很遗憾，没有人答对~'
            else:
                user_card_dict = await get_user_card_dict(bot, ev.group_id)
                msg_part = f'一共{len(winner_recorder.winner)}人答对，真厉害！他们是:\n' + '\n'.join([uid2card(uid, user_card_dict) for uid in winner_recorder.winner])
            
            if sv.bot.config.USE_CQPRO:
                dir_path = os.path.join(hoshino_res_path, 'img', 'priconne', 'unit')
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                cqcode = '' if not c.icon.exist else c.icon.cqcode
            else:
                cqcode = ''
            msg =  f'正确答案是: {c.name}{cqcode}\n{msg_part}'
            await bot.send(ev, msg)
            winner_recorder.turn_off()
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    try:
        if winner_recorder.get_on_off_status():
            s = ev.message.extract_plain_text()
            cid = chara.name2id(s)
            if cid != chara.UNKNOWN and cid == winner_recorder.correct_chara_id:
                winner_recorder.record_winner(ev.user_id)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))