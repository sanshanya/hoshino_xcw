from dataclasses import dataclass
from typing import List, Union

import re, asyncio, os, json
from bs4 import BeautifulSoup
from selenium import webdriver

import hoshino
from hoshino import Service, priv, aiorequests
from hoshino.modules.priconne.news import BaseSpider, Item
from hoshino.typing import CQEvent

sv_help = '''
启用nga会战爬虫 [国服/日服/台服] | 启用nga会战爬虫并设置爬取版块为:国服讨论/日服讨论/台服讨论，默认是国服讨论，每隔一段时间爬虫将自动爬取nga会战相关帖子
禁用nga会战爬虫 | 关闭nga会战爬虫服务
'''.strip()

sv = Service(
    name = 'nga会战爬虫',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '会战', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助nga会战爬虫"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


URL_CN = 'https://bbs.nga.cn/thread.php?stid=20775069'
URL_JP = 'https://ngabbs.com/thread.php?stid=20774924'
URL_TW = 'https://ngabbs.com/thread.php?fid=739'
ADDITIONAL_CLAN_BATTLE_KEYWORDS = ['周目', '排刀', '筛刀', '尾刀', '补偿刀', '补时刀', '挂树', '弟弟刀', '物理刀', '法刀', '白羊座', '金牛座', '双子座', '巨蟹座',
                       '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']


@dataclass
class Item:
    idx: Union[str, int]
    title: str = ""
    content: str = ""

    def __eq__(self, other):
        return self.idx == other.idx


class NGASpider(BaseSpider):
    url = {'cn': URL_CN, 'jp': URL_JP, 'tw': URL_TW}
    src_name = "nga会战爬虫"
    cookies = {}
    idx_cache = {'cn': [], 'jp': [], 'tw': []}
    item_cache = {'cn': [], 'jp': [], 'tw': []}

    @classmethod
    def set_cookies(cls, cookies):
        cls.cookies = cookies

    @classmethod
    async def get_response(cls, section) -> aiorequests.AsyncResponse:
        resp = await aiorequests.get(url = cls.url[section], cookies = cls.cookies)
        resp.raw_response.encoding = 'gbk'
        resp.raise_for_status()
        return resp

    @classmethod
    async def get_update(cls, section) -> List[Item]:
        resp = await cls.get_response(section)
        items = await cls.get_items(resp)
        updates = [i for i in items if has_clan_battle_keyword(i.title) and i.idx not in cls.idx_cache[section]]
        if updates:
            cls.idx_cache[section].extend([i.idx for i in updates])
        return updates

    @staticmethod
    async def get_items(resp: aiorequests.AsyncResponse):
        soup = BeautifulSoup(await resp.text, 'lxml')
        return [
            Item(idx=result['href'].split('=')[1],
                 title=result.get_text(),
                 content="{}\n{}".format(
                     result.get_text(), 'https://bbs.nga.cn' + result['href'])
                 ) for result in soup.find_all(class_='topic')
        ]

    @classmethod
    def format_items(cls, items):
        contents = [i.content for i in items]
        return f'{cls.src_name}在首页发现{len(contents)}个新的帖子:\n' + '\n'.join(contents)


def load_file(filename, default_obj = {}):
    try:
        file_path = f'./hoshino/modules/ngaclanbattlespider/{filename}'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as file:
                return json.load(file)
        else:
            return default_obj
    except:
        return default_obj


def save_file(obj, filename):
    try:
        with open(f'./hoshino/modules/ngaclanbattlespider/{filename}', 'w', encoding='utf8') as file:
            json.dump(obj, file, ensure_ascii=False, indent=4)
        return True
    except:
        return False


def has_clan_battle_keyword(string):
    has_keyword1 = re.search('[一二三四五12345]王', string)
    if has_keyword1 is not None:
        return True
    has_keyword2 = re.search('[ABCDabcd][123456]', string)
    if has_keyword2 is not None:
        return True
    has_keyword3 = re.search('[一二三四1234][阶段]', string)
    if has_keyword3 is not None:
        return True
    for key_word in ADDITIONAL_CLAN_BATTLE_KEYWORDS:
        if key_word in string:
            return True
    return False


async def spider_work(spider: BaseSpider, bot, section, broadcast_groups, sv: Service, TAG):
    updates = await spider.get_update(section)
    if not updates:
        sv.logger.info(f'{TAG}({section})未检索到新帖子')
        return
    sv.logger.info(f'{TAG}({section})检索到{len(updates)}个新帖子！')
    msg = spider.format_items(updates)
    for gid in broadcast_groups:
        await bot.send_group_msg(group_id=int(gid), message=msg)


def get_broadcast_groups():
    config = load_file('spider_config.json')
    broadcast_groups = {}
    broadcast_groups['cn'] = [gid for gid in config.keys() if config[gid]=='国服']
    broadcast_groups['jp'] = [gid for gid in config.keys() if config[gid]=='日服']
    broadcast_groups['tw'] = [gid for gid in config.keys() if config[gid]=='台服']
    return broadcast_groups


async def get_nga_cookies():
    driver = webdriver.Chrome()
    driver.get(URL_CN)
    await asyncio.sleep(5)
    cookies = driver.get_cookies()
    driver.quit()
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict


@sv.on_prefix(('启用nga会战爬虫', '启动nga会战爬虫', '开启nga会战爬虫'))
async def turn_on_spider(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    config = load_file('spider_config.json')
    gid = str(ev.group_id)
    s = ev.message.extract_plain_text()
    if s == '':
        s = config[gid].replace('(已禁用)', '') if config.get(gid) is not None else '国服'
    if s not in ['国服', '日服', '台服']:
        await bot.finish(ev, '错误: 参数请从"国服"/"日服"/"台服"中选择')
    else:
        section = s
    config[gid] = section
    if save_file(config, 'spider_config.json'):
        await bot.send(ev, f'nga会战爬虫已启用(爬取版面:{section}讨论)')
    else:
        await bot.send(ev, '启用nga会战爬虫失败，请重试')


@sv.on_fullmatch(('关闭nga会战爬虫', '禁用nga会战爬虫'))
async def turn_off_spider(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    config = load_file('spider_config.json')
    gid = str(ev.group_id)
    if config.get(gid) is not None and not config[gid].endswith('(已禁用)'):
        config[gid] += '(已禁用)'
    if save_file(config, 'spider_config.json'):
        await bot.send(ev, 'nga会战爬虫已禁用')
    else:
        await bot.send(ev, '禁用nga会战爬虫失败，请重试')


@sv.scheduled_job('cron', minute='*/5', second='15', jitter=20)
async def nga_spider():
    broadcast_groups = get_broadcast_groups()
    if not (broadcast_groups['cn'] or broadcast_groups['jp'] or broadcast_groups['tw']):
        return
    bot = hoshino.get_bot()
    NGASpider.set_cookies(await get_nga_cookies())
    for section in broadcast_groups.keys():
        if broadcast_groups[section]:
            if not NGASpider.idx_cache[section]:
                NGASpider.idx_cache[section] = load_file(f'idx_cache_{section}.json', [])
            await spider_work(NGASpider, bot, section, broadcast_groups[section], sv, 'nga会战爬虫')
            save_file(NGASpider.idx_cache[section], f'idx_cache_{section}.json')
