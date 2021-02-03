# Partially refer to the code of priconne games in HoshinoBot by @Ice-Cirno
# Under GPL-3.0 License

import asyncio
import os
import random
import aiohttp
import requests
from bs4 import BeautifulSoup

import hoshino
from hoshino import Service, priv, jewel
from hoshino.modules.priconne import chara
from hoshino.typing import MessageSegment, CQEvent
from . import GameMaster


sv_help = '''
- [cygames] 猜猜随机的"cygames"语音来自哪位角色
- [猜语音] 猜猜随机的语音来自哪位角色
'''.strip()

sv = Service(
    name = '猜语音',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助猜语音"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

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
        await bot.send(ev, f'下载完毕，此次下载"cygames"语音包{count}个，目前共{len(os.listdir(DIR_PATH))}个. 如果您使用的是go-cqhttp，请用软件将它们批量转换为silk格式，否则无法发送.')


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


@sv.on_prefix('cygames')
async def cygames_voice_guess(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        await download_voice_ci(bot, ev, sv.logger)
        file_list = os.listdir(DIR_PATH)
        chosen_file = random.choice(file_list)
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

@sv.on_prefix('猜语音')
async def voice_guess(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        record_path = os.path.join(HOSHINO_RES_PATH, 'record')
        if not os.path.exists(record_path):
            await cygames_voice_guess(bot, ev)
            return
        file_list = os.listdir(record_path)
        chosen_chara = random.choice(file_list)
        chara_path = os.path.join(HOSHINO_RES_PATH, 'record', chosen_chara)
        chara_list = os.listdir(chara_path)
        chosen_file = random.choice(chara_list)
        file_path = os.path.join(chara_path, chosen_file)
        await bot.send(ev, f'猜猜这段语音来自哪位角色? ({ONE_TURN_TIME}s后公布答案)')
        await bot.send(ev, MessageSegment.record(f'file:///{os.path.abspath(file_path)}'))
        #兼容"小仓唯骂我"插件的语音资源
        if chosen_chara == 'mawo':
            game.answer = 1036
        else:
            game.answer = int(chosen_chara)
        #print(chara.fromid(game.answer).name)
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
        jewel_counter = jewel.jewelCounter()
        winning_jewel = 70
        jewel_counter._add_jewel(ev.group_id, ev.user_id, winning_jewel)
        msg_part2 = f'获得了{winning_jewel}宝石'
        msg = f"正确答案是: {c.name}{c.icon.cqcode}\n{MessageSegment.at(ev.user_id)}猜对了，真厉害！TA已经猜对{n}次了~\n{msg_part2}"
        await bot.send(ev, msg)
