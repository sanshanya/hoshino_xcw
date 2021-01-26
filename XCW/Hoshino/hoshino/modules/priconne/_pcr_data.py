import os
import json


CHARA_NAME = {}
CHARA_PROFILE = {}

class CharaMaster:
    def __init__(self) -> None:
        self.chara_name_path = os.path.join(os.path.dirname(__file__), 'CHARA_NAME.json')
        self.chara_profile_path = os.path.join(os.path.dirname(__file__), 'CHARA_PROFILE.json')
        self.__load_pcr_data()
        self.__selfcheck()

    def __selfcheck(self) -> None:
        for chara_id in CHARA_NAME:
            if "" in CHARA_NAME[chara_id]:
                CHARA_NAME[chara_id].remove("")
        self.__save_pcr_data()


    def __load_pcr_data(self) -> None:
        # load CHARA_NAME
        with open(self.chara_name_path, 'r', encoding='utf-8') as f:
            chara_name_str = json.load(f)
        global CHARA_NAME
        for id in chara_name_str:
            CHARA_NAME[int(id)] = chara_name_str[id]
        
        # load CHARA_PROFILE
        with open(self.chara_profile_path, 'r', encoding='utf-8') as f:
            chara_profile_str = json.load(f)
        global CHARA_PROFILE
        for id in chara_profile_str:
            CHARA_PROFILE[int(id)] = chara_profile_str[id]


    def __save_pcr_data(self) -> None:
        # save CHARA_NAME
        with open(self.chara_name_path, 'w+', encoding='utf-8') as f:
            json.dump(CHARA_NAME, f, indent=4, ensure_ascii=False)

        # save CHARA_PROFILE
        with open(self.chara_profile_path, 'w+' , encoding='utf-8') as f:
            json.dump(CHARA_PROFILE, f, indent=4, ensure_ascii=False)


    def check_nickname(self, id:int, nickname:str):
        '''
        Return true if nickname already existed.
        '''
        if id not in CHARA_NAME:
            return None
        nicknames = CHARA_NAME[id]
        if nickname in nicknames:
            return True
        else:
            return False

    def add_chara(self, id:int, names:list) -> None:
        CHARA_NAME[id] = names
        self.__save_pcr_data()


    def add_nickname(self, id:int, nickname:str) -> None:
        CHARA_NAME[id].append(nickname)
        self.__save_pcr_data()


# CHARA_NAME will be loaded while init
chara_master = CharaMaster()

