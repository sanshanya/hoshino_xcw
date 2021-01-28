from hoshino import Service, priv
from .spider import *

svtw = Service(
    name = '台服官网新闻',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '订阅', #属于哪一类
    help_ = '台服官网新闻' #帮助文本
    )
svbl = Service(
    name = 'B服官网新闻',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '订阅', #属于哪一类
    help_ = 'B服官网新闻' #帮助文本
    )


async def news_poller(spider:BaseSpider, sv:Service, TAG):
    if not spider.item_cache:
        await spider.get_update()
        sv.logger.info(f'{TAG}新闻缓存为空，已加载至最新')
        return
    news = await spider.get_update()
    if not news:
        sv.logger.info(f'未检索到{TAG}新闻更新')
        return
    sv.logger.info(f'检索到{len(news)}条{TAG}新闻更新！')
    await sv.broadcast(spider.format_items(news), TAG, interval_time=0.5)
    
@svtw.scheduled_job('cron', minute='*/5', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, '台服官网')

@svbl.scheduled_job('cron', minute='*/5', jitter=20)
async def bili_news_poller():
    await news_poller(BiliSpider, svbl, 'B服官网')


async def send_news(bot, ev, spider:BaseSpider, max_num=5):
    if not spider.item_cache:
        await spider.get_update()
    news = spider.item_cache
    news = news[:min(max_num, len(news))]
    await bot.send(ev, spider.format_items(news), at_sender=True)

@svtw.on_fullmatch(('台服新闻', '台服日程'))
async def send_sonet_news(bot, ev):
    await send_news(bot, ev, SonetSpider)

@svbl.on_fullmatch(('B服新闻', 'b服新闻', 'B服日程', 'b服日程'))
async def send_bili_news(bot, ev):
    await send_news(bot, ev, BiliSpider)
