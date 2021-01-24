import re, hoshino, os, json

from . import RSS_class, rsshub
from hoshino import Service, priv
from hoshino.typing import CQEvent
from .config import *

sv_help = '''
- [添加订阅 订阅名 RSS地址(/twitter/user/username)]
- [删除订阅 订阅名]
- [查看所有订阅]
'''.strip()

sv = Service(
    name = '推特订阅',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '订阅', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助推特订阅"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


def load_config():
    try:
        config_path = hoshino_path + 'twitter_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf8') as config_file:
                return json.load(config_file)
        else:
            return {}
    except:
        return {}

def save_config(config):
    try:
        with open(hoshino_path + 'twitter_config.json', 'w', encoding='utf8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        return True
    except:
        return False


async def spider_work(rss, bot, sv:Service):
    updates = await rsshub.getRSS(rss)
    if not updates:
        sv.logger.info(f'{rss.url}未检索到新推文')
        return
    sv.logger.info(f'{rss.url}检索到{len(updates)}个新推文！')

    for msg in updates:
        for gid in rss.gid:
            await bot.send_group_msg(group_id=int(gid), message=msg)
            

@sv.on_prefix('添加订阅')
async def handle_RssAdd(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    s = ev.message.extract_plain_text().split(' ')
    try:
        name = s[0]
        url = s[1]
    except:
        await bot.send(ev, '输入参数缺失！')
        return

    config = load_config()
    gid = str(ev.group_id)
    if url in config.keys():
        gidList = []
        for item in config[url]:
            gidList.append(item[0])
        if gid not in gidList:
            config[url].append([gid,name])
        else:
            await bot.finish(ev, '此群已经添加过该订阅，请勿重复添加')
    else:
        config[url] = []
        config[url].append([gid,name])
    
    if save_config(config):
        await bot.send(ev, f'添加订阅"{s}"成功!')
        # 重新加载缓存
        await twitter_search_spider()
    else:
        await bot.send(ev, '添加订阅失败，请重试')


@sv.on_prefix('删除订阅')
async def handle_RssDel(bot, ev: CQEvent):
    config = load_config()
    s = ev.message.extract_plain_text()
    gid = str(ev.group_id)
    for url in config.keys():
        for item in config[url]:
            if item[0] == gid and s == item[1]:
                config[url].remove(item)
                msg = f'删除订阅"{s}"成功'
                if not save_config(config):
                    await bot.finish(ev, '删除订阅失败，请重试')
                await bot.send(ev, msg)
                return
    msg = f'删除失败, 此群未设置订阅"{s}"'
    await bot.send(ev, msg)
    

@sv.on_fullmatch('查看所有订阅')
async def handle_RssLook(bot, ev: CQEvent):
    config = load_config()
    gid = str(ev.group_id)
    msg = '' 
    for url in config.keys():
        for item in config[url]:
            if item[0] == gid:
                msg = msg + '\n' + item[1] + ': ' + url
    if msg == '':
        msg = '此群还未添加twitter订阅'
    else:
        msg = 'twitter爬虫已开启!\n此群设置的订阅为:'  + msg
    await bot.send(ev, msg)

@sv.scheduled_job('interval',minutes=5)
async def twitter_search_spider():
    bot = hoshino.get_bot()
    config = load_config()
    for url in config.keys():
        gid = []
        for item in config[url]:
            gid.append(item[0])
        if gid:
            rss = RSS_class.rss()
            rss.url = url
            rss.gid = gid
            await spider_work(rss, bot, sv)
    for root, dirs, files in os.walk(hoshino_path):
        for name in files:
            if name.endswith('.jpg'):
                os.remove(os.path.join(root, name))
    