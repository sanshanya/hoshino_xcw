import requests
from hoshino import Service
from nonebot import on_command

sv = Service('网抑云时间', visible= True, enable_on_default= True, bundle='网抑云时间', help_='''
- [上号/生而为人]
'''.strip())

@on_command('网抑云时间', aliases=('上号','生而为人','生不出人','网抑云','已黑化'), only_to_me=False)
async def music163_sentences(session):
    resp = requests.get('http://api.heerdev.top/nemusic/random',timeout=30)
    if resp.status_code == requests.codes.ok:
        res = resp.json()
        sentences = res['text']
        await session.send(sentences, at_sender=True)
    else:
        await session.send('上号失败，我很抱歉。您不pay被抑郁。', at_sender=True)