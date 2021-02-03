import asyncio
import os
import random

from hoshino import Service, priv, util, jewel
from hoshino.typing import MessageSegment, CQEvent
from . import game_util, GameMaster

sv_help = '''
- [神经衰弱] 开启一局公主连结主题的神经衰弱小游戏
- [神经衰弱排行] 查看神经衰弱小游戏群排行
'''.strip()

sv = Service(
    name = '神经衰弱',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助神经衰弱"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    



# 神经衰弱(Neurasthenia)小游戏相关参数
ROW_NUM = 4
COL_NUM = 4
SHOW_TIME = 6
ANSWER_TIME = 15
TOTAL_PIC_NUM = ROW_NUM * COL_NUM
DB_PATH = os.path.expanduser("~/.hoshino/pcr_neurasthenia.db")
assert TOTAL_PIC_NUM % 2 == 0

gm = GameMaster(DB_PATH)


@sv.on_fullmatch(("神经衰弱排行", "神经衰弱排行榜", "神经衰弱群排行"))
async def neurasthenia_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【神经衰弱小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, score = item
        m = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=uid)
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名: {name}, 总分: {score}分")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch('神经衰弱')
async def neurasthenia_game(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        chosen_ids = random.sample(game_util.VALID_IDS, TOTAL_PIC_NUM // 2)
        chosen_ids.extend(chosen_ids)
        random.shuffle(chosen_ids)
        # 记忆阶段
        await bot.send(ev, f'记忆阶段: ({SHOW_TIME}s后我会撤回图片哦~)')
        pic = MessageSegment.image(util.pic2b64(game_util.generate_full_pic(ROW_NUM, COL_NUM, chosen_ids)))
        msg = await bot.send(ev, pic)
        await asyncio.sleep(SHOW_TIME)
        await bot.delete_msg(message_id=msg['message_id'])
        await asyncio.sleep(2)
        # 回答阶段
        displayed_sub_pic_index = random.randint(0, TOTAL_PIC_NUM - 1)
        chosen_id = chosen_ids[displayed_sub_pic_index]
        explanation = game_util.EXPLANATION[chosen_id]
        ids = [game_util.JUMP_ID if i != displayed_sub_pic_index else id for i, id in enumerate(chosen_ids)]
        pic = MessageSegment.image(util.pic2b64(game_util.generate_full_pic(ROW_NUM, COL_NUM, ids, True)))
        await bot.send(ev, f'请告诉我另一个"{explanation}"所在位置的编号~ ({ANSWER_TIME}s后公布答案){pic}')
        game.answer = [i for i, id in enumerate(chosen_ids) if i != displayed_sub_pic_index and id == chosen_id][0] + 1
        await asyncio.sleep(ANSWER_TIME)
        # 结算
        game.update_score()
        msg_part1 = f'{MessageSegment.at(game.winner[0])}首先答对，真厉害~ 加2分! 当前总分为{game.get_first_winner_score()}分' if game.winner else ''
        msg_part2 = f'{game_util.generate_at_message_segment(game.winner[1:])}也答对了, 加1分~' if game.winner[1:] else ''
        msg_part3 = f'{game_util.generate_at_message_segment(game.loser)}答错了, 扣1分o(╥﹏╥)o' if game.loser else ''
        msg_part4 = '咦, 这轮游戏没人参与, 看来题目可能有点难...' if not (msg_part1 or msg_part2 or msg_part3) else ""
        msg_part = '\n'.join([s for s in [msg_part1, msg_part2, msg_part3, msg_part4] if s])
        await bot.send(ev, f'正确答案是: {game.answer}{MessageSegment.image(util.pic2b64(game_util.generate_full_pic(ROW_NUM, COL_NUM, chosen_ids)))}{msg_part}')


@sv.on_message()
async def on_input_index(bot, ev: CQEvent):
    game = gm.get_game(ev.group_id)
    if not game or game.answer == -1 or not ev.message.extract_plain_text().isdigit():
        return
    if int(ev.message.extract_plain_text()) == game.answer:
        game.record_winner(ev.user_id)
    else:
        game.record_loser(ev.user_id)

