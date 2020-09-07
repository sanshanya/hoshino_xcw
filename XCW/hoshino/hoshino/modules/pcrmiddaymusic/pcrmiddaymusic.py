import asyncio, json, os, random

import hoshino
from hoshino import Service, aiorequests
from hoshino.modules.pcrmiddaymusic import _song_data
from hoshino.typing import CQEvent, MessageSegment

sv = Service('pcr-midday-music', bundle='pcr娱乐', help_='''
每日午间自动推送pcr相关音乐, 也可直接在群内发送"来点音乐"请求pcr歌曲
'''.strip())

config_using = set()
CONFIG_PATH = './hoshino/modules/pcrmiddaymusic/pushed_music.json'


class Config:
    def __init__(self, gid, config_path):
        self.gid = str(gid)
        self.config_path = config_path

    def __enter__(self):
        config_using.add(self.gid)
        return self

    def __exit__(self, type, value, trace):
        if self.gid in config_using:
            config_using.remove(self.gid)

    def load(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf8') as config_file:
                    return json.load(config_file)
            else:
                return {}
        except:
            return {}

    def save(self, config):
        try:
            with open(self.config_path, 'w', encoding='utf8') as config_file:
                json.dump(config, config_file, ensure_ascii=False, indent=4)
            return True
        except:
            return False

    def load_pushed_music(self):
        config = self.load()
        return config[self.gid] if self.gid in config else []

    def save_pushed_music(self, pushed_music):
        config = self.load()
        config[self.gid] = pushed_music
        return self.save(config)


async def get_pic_url(bv):
    url = f'https://api.bilibili.com/x/web-interface/view?bvid={bv}'
    resp = await aiorequests.get(url)
    content = await resp.json()
    return content['data']['pic']


async def get_next_song(gid):
    with Config(gid, CONFIG_PATH) as config:
        pushed_music = config.load_pushed_music()
        song_dict = _song_data.SONG_DATA
        songs = list(song_dict.keys())
        random.shuffle(songs)
        all_pushed = True
        for song in songs:
            if song not in pushed_music:
                all_pushed = False
                break
        if all_pushed:
            song = songs[0]
            pushed_music = []
        song_data = song_dict[song]
        pic_url = await get_pic_url(song_data[5]) if song_data[5] else ""
        img = MessageSegment.image(pic_url) if pic_url else ""
        msg_part = '' if song_data[6]=='' else '\n-------------------------------------------\n'
        song_info = song_data[2] + song + str(img) + '歌曲名: ' + song_data[3] + '\n' + '歌手: ' + song_data[4] + msg_part + song_data[6]
        pushed_music.append(song)
        config.save_pushed_music(pushed_music)
    return song_info, song_data


@sv.on_fullmatch('来点音乐')
async def music_push(bot, ev: CQEvent):
    if ev.group_id in config_using:
        return
    song_info, song_data = await get_next_song(ev.group_id)
    if song_data[0] == 'bili':
        song_link = f'\nhttps://www.bilibili.com/video/{song_data[1]}'
    elif song_data[0] == 'qq':
        song_link = f'\nhttps://i.y.qq.com/v8/playsong.html?_wv=1&songid={song_data[1]}&souce=qqshare&source=qqshare&ADTAG=qqshare'
    elif song_data[0] == '163':
        song_link = f'\nhttp://music.163.com/m/song/{song_data[1]}'
    else:
        song_link = ''
    await bot.send(ev, song_info+song_link)


@sv.scheduled_job('cron', hour=12, minute=9, jitter=30)
async def music_daily_push():
    bot = hoshino.get_bot()
    glist = await sv.get_enable_groups()
    info_head = '今日份的午间音乐广播~'
    for gid, selfids in glist.items():
        song_info, song_data = await get_next_song(gid)
        if song_data[0] == 'bili':
            music = MessageSegment.share(url='https://www.bilibili.com/video/'+song_data[1], title = song_data[3], content = song_data[4], image_url = "http://i0.hdslb.com/bfs/archive/b28c463d04db58f6eb79e238757b78ab1f609ec0.png")
        else:
            music = MessageSegment.music(type_=song_data[0], id_=song_data[1])
        await bot.send_group_msg(self_id=random.choice(selfids), group_id=gid, message=info_head+song_info)
        await bot.send_group_msg(self_id=random.choice(selfids), group_id=gid, message=music)
        await asyncio.sleep(0.5)