# hoshino\modules\priconne\query\query.py
# 从priconne/quick读取rxx-xx-server.png文件名rank图并发送
from hoshino import util, R
import os
import re
from hoshino.modules.hoshino_training.util.rex import *

def get_rank_pic(server='cn'):
    path = f'priconne/quick'
    res = R.img(path)
    if not os.path.exists(res.path):
        return None
    fnlist = os.listdir(res.path)
    rank_list = []
    maxn = 0
    for fn in fnlist:
        if fn[0] != 'r' and fn[0] != 'R':
            continue
        args = re.split(r'\.|-', fn[1:])
        if len(args) < 4 or args[2] != server or not args[0].isdigit() or not args[1].isdigit():
            continue
        n = int(args[0]) * 10 + int(args[1])
        if n > maxn:
            maxn = n
            rank_list = [fn]
        elif n == maxn:
            rank_list.append(fn)
    rank_list.sort()
    return rank_list

async def rank_sheet(bot, ev):
    match = ev['match']
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev, '\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*陆rank表', at_sender=True)
        return
    msg = [
        '\n※表格仅供参考，升r有风险，强化需谨慎\n※一切以会长要求为准——',
    ]
    if is_jp:
        flist = get_rank_pic('jp')
        if len(flist) == 0:
            await bot.send(ev, '无数据', at_sender=True)
            return
        args = re.split(r'\.|-', flist[0])
        msg.append(f'※不定期搬运自图中Q群\n※广告为原作者推广，与本bot无关\n{args[0]}-{args[1]} rank表：')
        pos = match.group(3)
        if not pos or '前' in pos:
            p = R.img('priconne/quick/' + flist[0]).cqcode
            msg.append(str(p))
        if len(flist) >= 2 and not pos or '中' in pos:
            p = R.img('priconne/quick/' + flist[1]).cqcode
            msg.append(str(p))
        if len(flist) >= 3 and not pos or '后' in pos:
            p = R.img('priconne/quick/' + flist[2]).cqcode
            msg.append(str(p))
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)
    elif is_tw:
        flist = get_rank_pic('tw')
        if len(flist) == 0:
            await bot.send(ev, '无数据', at_sender=True)
            return
        args = re.split(r'\.|-', flist[0])
        msg.append(f'※不定期搬运自漪夢奈特\n※油管频道有介绍视频及原文档\n{args[0]}-{args[1]} rank表：')
        for fn in flist:
            p = R.img('priconne/quick/' + fn).cqcode
            msg.append(f'{p}')
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)
    elif is_cn:
        flist = get_rank_pic('cn')
        if len(flist) == 0:
            await bot.send(ev, '无数据', at_sender=True)
            return
        args = re.split(r'\.|-', flist[0])
        msg.append(f'※不定期搬运自NGA\n{args[0]}-{args[1]} rank表：')
        for fn in flist:
            p = R.img('priconne/quick/' + fn).cqcode
            msg.append(f'{p}')
        await bot.send(ev, '\n'.join(msg), at_sender=True)
        await util.silence(ev, 60)

rex_replace(r'^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$', rank_sheet)