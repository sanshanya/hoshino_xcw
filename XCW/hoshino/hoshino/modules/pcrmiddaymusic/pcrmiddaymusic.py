import asyncio, json, os, random

import hoshino
from hoshino import Service, priv, aiorequests
from hoshino.modules.pcrmiddaymusic import _song_data
from hoshino.typing import CQEvent, MessageSegment

sv_help = '''
每日午间自动推送pcr相关音乐, 也可直接在群内发送"来点音乐"请求pcr歌曲
'''.strip()

sv = Service(
    name = '午间音乐',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '订阅', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助午间音乐"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


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


async def get_song_info_from_song(song):
    song_data = _song_data.SONG_DATA[song]
    pic_url = await get_pic_url(song_data[5]) if song_data[5] else ""
    img = MessageSegment.image(pic_url) if pic_url else ""
    msg_part = '' if song_data[6] == '' else '\n-------------------------------------------\n'
    song_info = song_data[2] + song + str(img) + '歌曲名: ' + song_data[3] + '\n' + '歌手: ' + song_data[4] + msg_part + \
                song_data[6]
    return song_info, song_data


async def get_next_song(gid):
    with Config(gid, CONFIG_PATH) as config:
        pushed_music = config.load_pushed_music()
        song_dict = _song_data.SONG_DATA
        not_pushed_music = set(song_dict.keys()) - set(pushed_music)
        if not_pushed_music:
            song = random.choice(list(not_pushed_music))
        else:
            song = random.choice(list(song_dict.keys()))
            pushed_music = []
        song_info, song_data = await get_song_info_from_song(song)
        pushed_music.append(song)
        config.save_pushed_music(pushed_music)
    return song_info, song_data


def get_music_from_song_data(song_data):
    if song_data[0] == 'bili':
        return MessageSegment.share(url='https://www.bilibili.com/video/' + song_data[1], title=song_data[3],
                                     content=song_data[4],
                                     image_url="http://i0.hdslb.com/bfs/archive/b28c463d04db58f6eb79e238757b78ab1f609ec0.png")
    elif song_data[0] == 'qq':
        return MessageSegment(type_='music',
                              data={
                                  'type': song_data[0],
                                  'id': str(song_data[1]),
                                  'content': song_data[4]
                              })
    else:
        return MessageSegment.music(type_=song_data[0], id_=song_data[1])


def keyword_search(keyword):
    song_dict = _song_data.SONG_DATA
    result = []
    for song in song_dict:
        if keyword in song or keyword in song_dict[song][3]:
            result.append(song)
    return result


@sv.on_prefix(('来点音乐', '来首音乐'))
async def music_push(bot, ev: CQEvent):
    if ev.group_id in config_using:
        return
    s = ev.message.extract_plain_text()
    if s:
        available_songs = keyword_search(s)
        if not available_songs:
            await bot.send(ev, f'未找到含有关键词"{s}"的歌曲...')
            return
        elif len(available_songs) > 1:
            msg_part = '\n'.join(['• ' + song for song in available_songs])
            await bot.send(ev, f'从曲库中找到了这些:\n{msg_part}\n您想找的是哪首呢~')
            return
        else:
            song_info, song_data =  await get_song_info_from_song(available_songs[0])
    else:
        song_info, song_data = await get_next_song(ev.group_id)
    await bot.send(ev, song_info)
    await bot.send(ev, get_music_from_song_data(song_data))


@sv.scheduled_job('cron', hour=12, minute=9)
async def music_daily_push():
    bot = hoshino.get_bot()
    glist = await sv.get_enable_groups()
    info_head = '今日份的午间音乐广播~'
    for gid, selfids in glist.items():
        song_info, song_data = await get_next_song(gid)
        sid = random.choice(selfids)
        await bot.send_group_msg(self_id=sid, group_id=gid, message=info_head+song_info)
        await bot.send_group_msg(self_id=sid, group_id=gid, message=get_music_from_song_data(song_data))
        await asyncio.sleep(2)