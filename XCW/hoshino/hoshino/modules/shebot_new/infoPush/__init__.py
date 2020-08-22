import nonebot
import re
from typing import Dict
from hoshino.util4sh import RSS, load_config, save_config, broadcast
from lxml import etree
from hoshino.service import Service
from os import path
from collections import defaultdict

class Info(RSS):
    def __init__(self,route) -> None:
        super().__init__()
        self.limit = 1 #info类信息只需一条
        self._latest : str = ''
        self.route = route
    
    def parse_xml(self) -> Dict:
        rss = etree.XML(self.xml)
        item = rss.xpath('/rss/channel/item')[0]
        title = item.find('.title').text.strip()
        desc = item.find('.description').text.strip()
        link = item.find('.link').text.strip()
        pubDate = item.find('.pubDate').text.strip()
        return {
            "title" : title,
            "desc" : desc,
            "link" : link,
            "pubDate" : pubDate
        }
    def check_update(self) -> bool: #info类可以通过pubDate判断是否更新
        if self.parse_xml().get('pubDate') != self._latest:
            self._latest = self.parse_xml().get('pubDate')
            return True
        else:
            return False          

#添加推送在此字典添加service和路由
_inf_svs = {
    Service('pcr国服推送') : [
        Info('/pcr/news-cn'), 
        Info('/bilibili/user/dynamic/353840826')
        ],
    Service('B站up动态') : [
        Info('/bilibili/user/dynamic/282994'), 
        Info('/bilibili/user/dynamic/11073'),
        Info('/bilibili/user/dynamic/673816')
        ]
    #Service('HoshinoIssue推送') : [Info('/github/issue/Ice-Cirno/Hoshinobot')]
}

_latest_path = path.join(path.dirname(__file__),'latest_data.json')
_latest_data = load_config(_latest_path) if load_config(_latest_path) else defaultdict(str)
infos = []

for sv in _inf_svs:
    infos.extend(_inf_svs[sv])

for info in infos:
    info._latest = _latest_data.get(info.route, '')

from hoshino.util4sh import Res as R
async def handle_xml_img(xml_str: str) -> str:
    for label in re.findall('<img src="(.+?)".+?>', xml_str):
        if re.search('(".+?")', label):
            url = re.search('(".+?")', label).group(1)
            pic = await R.image_from_url(url)
            xml_str = re.sub('<.+?>', str(pic), xml_str, 1)
    return xml_str

@nonebot.scheduler.scheduled_job('cron', minute='*/5', second='30')
async def check():
    for sv in _inf_svs:
        for info in _inf_svs[sv]:
            try:
                await info.get()
            except Exception as ex:
                sv.logger.error(ex)
            if info.check_update():
                _latest_data[info.route] = info._latest
                save_config(_latest_data, _latest_path)
                sv.logger.info(f'检查到{sv.name}消息更新')
                data = info.parse_xml()
                title = data['title']
                link = data['link']
                await broadcast(f'{title}\n{link}',sv_name=sv.name)
            else:
                sv.logger.info(f'未检查到{sv.name}消息更新')

