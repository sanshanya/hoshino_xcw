"""无损音乐搜索 数据来自acgjc.com"""
from hoshino import Service, priv, logger, aiorequests
from hoshino.typing import CQEvent
from urllib.parse import quote

sv_help = '''
无说明
'''.strip()

sv = Service(
    name = '搜无损音乐',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = False, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助搜无损音乐"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


@sv.on_prefix('搜无损')
async def search_flac(bot, ev: CQEvent):
    keyword = ev.message.extract_plain_text()
    resp = await aiorequests.get('http://mtage.top:8099/acg-music/search', params={'title-keyword': keyword}, timeout=1)
    res = await resp.json()
    if res['success'] is False:
        logger.error(f"Flac query failed.\nerrorCode={res['errorCode']}\nerrorMsg={res['errorMsg']}")
        await bot.finish(ev, f'查询失败 请至acgjc官网查询 www.acgjc.com/?s={quote(keyword)}', at_sender=True)

    music_list = res['result']['content']
    music_list = music_list[:min(5, len(music_list))]

    details = [" ".join([
        f"{ele['title']}",
        f"{ele['downloadLink']}",
        f"密码：{ele['downloadPass']}" if ele['downloadPass'] else ""
    ]) for ele in music_list]

    msg = [
        f"共 {res['result']['totalElements']} 条结果" if len(music_list) > 0 else '没有任何结果',
        *details,
        '数据来自 www.acgjc.com',
        f'更多结果可见 www.acgjc.com/?s={quote(keyword)}'
    ]

    await bot.send(ev, '\n'.join(msg), at_sender=True)
