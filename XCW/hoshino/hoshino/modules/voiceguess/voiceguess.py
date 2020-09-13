# Partially refer to the code of priconne games in HoshinoBot by @Ice-Cirno
# Under GPL-3.0 License

import asyncio
import os
import random
import aiohttp
import requests
from bs4 import BeautifulSoup

import hoshino
from hoshino import Service
from hoshino.modules.priconne import chara
from hoshino.typing import MessageSegment, CQEvent
from . import GameMaster


sv = Service('voiceguess', bundle='pcr娱乐', help_='''
[cygames] 猜猜随机的"cygames"语音来自哪位角色
'''.strip())

DOWNLOAD_THRESHOLD = 76
MULTIPLE_VOICE_ESTERTION_ID_LIST = ['0044']
ONE_TURN_TIME = 30
HOSHINO_RES_PATH = os.path.expanduser(hoshino.config.RES_DIR)
DIR_PATH = os.path.join(HOSHINO_RES_PATH, 'voice_ci')
DB_PATH = os.path.expanduser("~/.hoshino/pcr_voice_guess.db")

gm = GameMaster(DB_PATH)


def get_estertion_id_list():
    url = 'https://redive.estertion.win/sound/vo_ci/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    l = []
    for a in soup.find_all('a'):
        s = a['href'][:-1]
        if s.isdigit():
            l.append(s)
    return l


def estertion_id2chara_id(estertion_id):
    return (estertion_id + 1000)


async def download(url, path):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return True
    except:
        return False


async def download_voice_ci(bot, ev: CQEvent, logger):
    if not os.path.exists(DIR_PATH):
        os.makedirs(DIR_PATH)
    file_name_list = os.listdir(DIR_PATH)
    file_name_list_no_suffix = [file.rsplit('.', 1)[0] for file in file_name_list]
    if len(file_name_list) < DOWNLOAD_THRESHOLD:
        count = 0
        await bot.send(ev, '正在下载"cygames"语音资源，请耐心等待')
        estertion_id_list = get_estertion_id_list()
        for eid in estertion_id_list:
            file_number_list = ['001'] if eid not in MULTIPLE_VOICE_ESTERTION_ID_LIST else ['001', '002']
            for file_number in file_number_list:
                url = f'https://redive.estertion.win/sound/vo_ci/{eid}/vo_ci_1{eid[1:]}01_{file_number}.m4a'
                file_name = url.split('/')[-1]
                if file_name.rsplit('.', 1)[0] not in file_name_list_no_suffix:
                    file_path = os.path.join(DIR_PATH, file_name)
                    logger.info(f'准备下载{file_name}...')
                    if not await download(url, file_path):
                        logger.info(f'下载{file_name}失败, 准备删除文件.')
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        logger.info(f'删除文件{file_name}成功.')
                    else:
                        logger.info(f'下载{file_name}成功!')
                        count = count + 1
        await bot.send(ev, f'下载完毕，此次下载"cygames"语音包{count}个，目前共{len(os.listdir(DIR_PATH))}个. 请使用软件将它们批量转换为silk格式.')


@sv.on_fullmatch(("猜语音排行", "猜语音排行榜", "猜语音群排行"))
async def description_guess_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【猜语音小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, count = item
        m = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=uid)
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名: {name}, 猜对{count}次")
    await bot.send(ev, "\n".join(msg))


@sv.on_prefix(('cygames', '猜语音'), only_to_me= False)
async def cygames_voice_guess(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        await download_voice_ci(bot, ev, sv.logger)
        file_list = os.listdir(DIR_PATH)
        chosen_file = random.choice(file_list)
        file_suffix = chosen_file.rsplit('.', 1)[1]
        if file_suffix != 'silk' and file_suffix != 'amr':
            await bot.send(ev, "警告: 发现非silk或amr格式的语音, 建议使用软件转成silk格式, 否则可能无法发送.")
        file_path = os.path.join(DIR_PATH, chosen_file)
        await bot.send(ev, f'猜猜这个“cygames”语音来自哪位角色? ({ONE_TURN_TIME}s后公布答案)')
        await bot.send(ev, MessageSegment.record(f'file:///{os.path.abspath(file_path)}'))
        estertion_id = chosen_file[7:10]
        chara_id = estertion_id2chara_id(int(estertion_id))
        game.answer = chara_id
        await asyncio.sleep(ONE_TURN_TIME)
        # 结算
        if game.winner:
            return
        c = chara.fromid(game.answer)
    await bot.send(ev, f"正确答案是: {c.name} {c.icon.cqcode}\n很遗憾，没有人答对~")


@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.winner:
        return
    c = chara.fromname(ev.message.extract_plain_text())
    if c.id != chara.UNKNOWN and c.id == game.answer:
        game.winner = ev.user_id
        n = game.record()
        gm.exit_game(ev.group_id)
        msg = f"正确答案是: {c.name}{c.icon.cqcode}\n{MessageSegment.at(ev.user_id)}猜对了，真厉害！TA已经猜对{n}次了~"
        await bot.send(ev, msg)
