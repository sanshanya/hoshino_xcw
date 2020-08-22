from hoshino.util4sh import RSS, load_config, save_config, broadcast
from nonebot import CommandSession
from os import path
from lxml import etree
from hoshino.service import Service

class Video:
    def __init__(self,title=None,desc=None,link=None,time=None):
        self.title = title
        self.desc = desc
        self.link = link
        self.time = time
    def __eq__(self, other):
        return self.time == other.time

class BiliVideo(RSS):
    def __init__(self,UID:int):
        super().__init__()
        self.route = f'/bilibili/user/video/{UID}'
        self.limit = 1
        self.UID = UID
        self.latest = Video()
    def parse_xml(self):
        rss = etree.XML(self.xml)
        item = rss.xpath('/rss/channel/item')[0]
        title = item.find('.title').text.strip()
        desc = item.find('.description').text.strip()
        link = item.find('.link').text.strip()
        time = item.find('.pubDate').text.strip()
        return Video(title,desc,link,time)

        

sv = Service('B站投稿提醒')
subs_path = path.join(path.dirname(__file__),'subs.json')
_subscribes = load_config(subs_path)
_BVs = []

for subs in _subscribes:
    UID = _subscribes[subs]['UID']
    BV = BiliVideo(UID)
    BV.latest.time = _subscribes[subs]['latest_time']
    _BVs.append(BV)

@sv.scheduled_job('cron',minute='*/10',second='20')
async def check_BiliVideo():
    for BV in _BVs:
        await BV.get()
        video = BV.parse_xml()
        if BV.latest != video: #投稿有更新
            sv.logger.info(f'检测到up{BV.UID}投稿更新')
            BV.latest = video
            global _subscribes
            _subscribes[str(BV.UID)]['latest_time'] = video.time
            save_config(_subscribes,subs_path)
            groups = _subscribes[str(BV.UID)]['subs_groups']
            await broadcast(f'up投稿提醒========\n{video.title}\n{video.link}',groups=groups)
        else:
            sv.logger.info(f'未检测到up{BV.UID}投稿更新')

@sv.on_command('video',aliases=('投稿提醒'))
async def subscribe(session:CommandSession):
    UID_str = session.get('UID',prompt='请输入订阅up的UID')
    if not UID_str.isdigit():
        del session.state['UID']
        session.pause('参数错误，请重新输入')
    global _subscribes
    gid = session.event['group_id']
    if UID_str in _subscribes.keys():
        if gid not in _subscribes[UID_str]['subs_groups']:
            _subscribes[UID_str]['subs_groups'].append(gid)
        else:
            await session.send('本群已经订阅过该UP了')
            return
    else:
        _subscribes[UID_str] = {
            "UID" : int(UID_str),
            "subs_groups" : [gid],
            "latest_time" : ""
        }
        BV = BiliVideo(int(UID_str))
        global _BVs
        _BVs.append(BV)
    if save_config(_subscribes,subs_path):
        await session.send('订阅成功')
    else:
        await session.send('订阅失败，请与bot维护中联系')

@sv.on_command('cancel_video',aliases=('取消UP投稿提醒','取消投稿提醒'))
async def cancel(session:CommandSession):
    UID_str = session.get('UID',prompt='请输入UID')
    global _subscribes
    global _BVs
    if UID_str in _subscribes.keys():
        if len(_subscribes[UID_str]['subs_groups']) ==1: #只有一个群订阅该up投稿
            for BV in _BVs[::-1]:
                if BV.UID == int(UID_str):
                    _BVs.remove(BV)
            del _subscribes[UID_str]
            save_config(_subscribes,subs_path)
            sv.logger.info(f'成功取消up{UID_str}的投稿提醒')
            session.send(f'成功取消up{UID_str}的投稿提醒')
        else:
            gid = session.event['group_id']
            _subscribes[UID_str]['subs_groups'].remove(gid)
            save_config(_subscribes,subs_path)
            session.send(f'成功取消up{UID_str}的投稿提醒')