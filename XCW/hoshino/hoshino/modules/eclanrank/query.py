from typing import List
import math
import json
import requests
from . import util

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
        uid: int = 0
) -> List[get_rank_response] or bool:
    last_api = ''
    last_req = {}
    if rank:
        last_api = '/rank/'
        rank = math.floor(int(rank))

    if name:
        last_api = '/name/'
        last_req = {'clanName': name.strip()}

    if leader:
        last_api = '/leader/'
        last_req = {'leaderName': leader.strip()}

    if score:
        last_api = '/score/'
        rank = math.floor(int(score))
    if not last_api:
        return False

    url = f'{config["rules"]["base_url"]}{last_api}{(rank if rank != -1 else 0)}'
    headers = config["rules"]["headers"]
    info = json.loads(requests.post(url, json=last_req, headers=headers, timeout=20).text)

    if info['code'] > 0:
        print(info['msg'])
        return False

    info = info['data']
    if uid:
        info = util.filter_list(info, lambda x: x['leader_viewer_id'] == uid)

    if not bool(info):
        return False

    return list(get_rank_response(i) for i in info)


def get_line() -> List or bool:
    url = f'{config["rules"]["base_url"]}/line'
    headers = config["rules"]["headers"]
    info = json.loads(requests.post(url, json={}, headers=headers, timeout=20).text)
    if info['code'] > 0:
        print(info['msg'])
        return False
    if not bool(info['data']):
        return False
    return info['data']
