from typing import List
import time
import datetime
import math
import json
import requests
from . import util
from nonebot.log import logger

config = util.get_config()


class get_rank_response:
    def __init__(self, data):
        self.data = data
        self.data['group_id'] = 0

    @property
    def rank(self) -> int:
        return self.data['rank']

    @property
    def damage(self) -> int:
        return self.data['damage']

    @property
    def clan_name(self) -> str:
        return self.data['clan_name']

    @property
    def member_num(self) -> int:
        return self.data['member_num']

    @property
    def leader_name(self) -> str:
        return self.data['leader_name']

    @property
    def leader_viewer_id(self) -> str:
        return self.data['leader_viewer_id']

    @property
    def group_id(self) -> int:
        return self.data['group_id']

    @group_id.setter
    def group_id(self, group_id):
        self.data['group_id'] = group_id


def get_rank(
        rank: int = 0,
        name: str = '',
        leader: str = '',
        score: int = 0,
        uid: int = 0,
        history: int = 0,
        ids: List[int] = None
) -> List[get_rank_response] or bool:
    last_api = ''
    last_req = {
        'history': history
    }
    if rank:
        last_api = '/rank/'
        rank = math.floor(int(rank))

    if name:
        last_api = '/name/'
        last_req['clanName'] = name.strip()

    if leader:
        last_api = '/leader/'
        last_req['leaderName'] = leader.strip()

    if score:
        last_api = '/score/'
        rank = math.floor(int(score))

    if ids:
        last_api = '/fav/'
        last_req['ids'] = ids

    if not last_api:
        return False, ''

    url = f'{config.rules.base_url}{last_api}{(rank if rank != -1 else 0)}'
    headers = config.rules.headers
    info = json.loads(requests.post(url, json=last_req, headers=headers, timeout=20).text)

    if info['code'] > 0:
        logger.info(info['msg'])
        return False, ''

    data = info['data']
    if uid:
        data = util.filter_list(data, lambda x: x['leader_viewer_id'] == uid)

    if not bool(data):
        return False, ''
    info['ts'] = info['ts'] if info['ts'] else time.time()
    return list(get_rank_response(i) for i in data), datetime.datetime.fromtimestamp(info['ts']).strftime(
        config.str.ts_formet)


def get_line() -> List or bool:
    url = f'{config.rules.base_url}/line'
    headers = config.rules.headers
    info = json.loads(requests.post(url, json={}, headers=headers, timeout=20).text)
    if info['code'] > 0:
        logger.info(info['msg'])
        return False
    if not bool(info['data']):
        return False
    return info['data']
