from hoshino import Service
import aiohttp

sv = Service('nbnhhsh', visible= True, enable_on_default= True, bundle='nbnhhsh', help_='''
[? XX] XX是你不理解的dx
'''.strip())


@sv.on_rex(r'^[\?\？]{1,2} ?([a-z0-9]+)$', normalize=True)
async def hhsh(bot,event):
    async with aiohttp.TCPConnector(verify_ssl=False) as connector:
        async with aiohttp.request(
            'POST',
            url='https://lab.magiconch.com/api/nbnhhsh/guess',
            json={"text": event.match.group(1)},
            connector=connector,
        ) as resp:
            j = await resp.json()
    if len(j) == 0:
        await bot.send(event, '没有结果',at_sender=True)
        return
    res = j[0]
    name=res.get('name')
    trans=res.get('trans','没有结果')
    msg = '{}: {}'.format(
        name,
        ' '.join(trans),
    )
    await bot.send(event,msg,at_sender=True)
