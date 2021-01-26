import nonebot
from hoshino import aiorequests
from hoshino.modules.hoshino_training.util.module import *
from hoshino.modules.hoshino_training.util.scheduler import *

#超时时间
timeout = 120

#代理, 必须使用http代理, 不使用请留空
proxy = ''
#proxy = 'http://172.17.0.1:1081'

proxies={
    'http': proxy,
    'https': proxy,
}

update_seeker = None

async def get(url, params=None, **kwargs):
    return None

class NewAaiorequests:
    def __init__(self):
        pass

    async def get(self, url, params=None, **kwargs):
        kwargs['timeout'] = timeout
        kwargs['proxies'] = proxies
        return await aiorequests.get(url, params=params, **kwargs)

@seheduler_func
async def new_update_seeker():
    global update_seeker
    if update_seeker:
        try:
            await update_seeker.__wrapped__()
        except:
            pass

new_aiorequests = NewAaiorequests()
module_replace('hoshino.modules.priconne.comic', 'aiorequests', new_aiorequests)

update_seeker = module_get('hoshino.modules.priconne.comic', 'update_seeker')
if update_seeker:
    scheduler_remove('hoshino.modules.priconne.comic:update_seeker')
    nonebot.scheduler.add_job(new_update_seeker, 'interval', minutes=5)