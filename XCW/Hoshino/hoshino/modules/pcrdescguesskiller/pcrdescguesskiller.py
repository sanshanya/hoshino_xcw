from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.modules.priconne import _pcr_data
from hoshino.modules.priconne import chara

import hoshino
import os

sv_help = '''
杀手~
'''.strip()

sv = Service(
    name = '猜角色杀手',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = False, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助猜角色杀手"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


BLOOD_TYPE = ''
ANSWERS_DIC_CACHE = {}
#INFO_LIST = {'名字':0, '公会':1, '生日':2, '年龄':3, '身高':4, '体重':5, '血型':6, '种族':7, '喜好':8, '声优':9}

class game_status:
    def __init__(self):
        self.on = {}
        
    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False

    def turn_on(self, gid):
        self.on[gid] = True
        global BLOOD_TYPE, ANSWERS_DIC_CACHE
        BLOOD_TYPE = ''
        ANSWERS_DIC_CACHE.clear()
        
    def turn_off(self, gid):
        self.on[gid] = False
        global BLOOD_TYPE, ANSWERS_DIC_CACHE
        BLOOD_TYPE = ''
        ANSWERS_DIC_CACHE.clear()

game_status = game_status()

@sv.on_fullmatch('5秒钟后每隔12秒我会给出某位角色的一个描述，根据这些描述猜猜她是谁~')
async def trun_on_killer(bot, ev: CQEvent):
    game_status.turn_on(ev.group_id)

@sv.on_message()
async def on_sended_chara_info(bot, ev: CQEvent):
    global BLOOD_TYPE, ANSWERS_DIC_CACHE
    try:
        if game_status.get_on_off_status(ev.group_id):
            s = ev.message.extract_plain_text()
            if '提示' and '她的' in s:
                chara_info = s.replace('提示','').replace('/5:','').replace('\n',' ').replace('她的','').replace('是','')
                chara_info_list = chara_info.split()
                #print(chara_info_list)
                if not len(ANSWERS_DIC_CACHE) == 0:
                    if chara_info_list[0]==5 and BLOOD_TYPE!='':
                        answers = {}
                        for cache_chara_id in ANSWERS_DIC_CACHE.keys(): 
                            if ANSWERS_DIC_CACHE[cache_chara_id]['血型'] == BLOOD_TYPE:
                                answers[cache_chara_id] = ANSWERS_DIC_CACHE[cache_chara_id]
                        ANSWERS_DIC_CACHE = answers
                    if chara_info_list[1] == '血型':
                        BLOOD_TYPE = chara_info_list[2]
                    else:
                        answers = {}
                        for chara_id in ANSWERS_DIC_CACHE.keys():
                            chara_properties = ANSWERS_DIC_CACHE[chara_id][chara_info_list[1]]
                            if chara_properties == chara_info_list[2]:
                                answers[chara_id] = ANSWERS_DIC_CACHE[chara_id]
                        ANSWERS_DIC_CACHE = answers
                else:
                    if chara_info_list[1] == '血型':
                        BLOOD_TYPE = chara_info_list[2]
                    else:
                        for chara_id in _pcr_data.CHARA_PROFILE.keys():
                            chara_properties = _pcr_data.CHARA_PROFILE[chara_id][chara_info_list[1]]
                            if chara_properties == chara_info_list[2]:
                                ANSWERS_DIC_CACHE[chara_id] = _pcr_data.CHARA_PROFILE[chara_id]
                if len(ANSWERS_DIC_CACHE)<4 and len(ANSWERS_DIC_CACHE)!=0:
                    answers = {}
                    if not BLOOD_TYPE == '':
                            for cache_chara_id in ANSWERS_DIC_CACHE.keys(): 
                                if ANSWERS_DIC_CACHE[cache_chara_id]['血型'] == BLOOD_TYPE:
                                    answers[cache_chara_id] = ANSWERS_DIC_CACHE[cache_chara_id]
                            ANSWERS_DIC_CACHE = answers
                    print(ANSWERS_DIC_CACHE)
                    for cache_chara_id in ANSWERS_DIC_CACHE.keys():
                        chara_name = chara.fromid(cache_chara_id).name
                        await bot.send(ev, chara_name)
                    game_status.turn_off(ev.group_id)
                #print(ANSWERS_DIC_CACHE)
            elif '猜对了，真厉害！' in s:
                game_status.turn_off(ev.group_id)
            elif '很遗憾，没有人答对~' in s:
                game_status.turn_off(ev.group_id)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))
