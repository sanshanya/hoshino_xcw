import asyncio
import os
import random

from hoshino import Service, priv, util
from hoshino.typing import MessageSegment, CQEvent
from . import game_util, GameMaster

sv_help = '''
- [完美配对] 开启一局公主连结主题的完美配対小游戏
- [完美配对排行] 查看完美配对小游戏群排行
'''.strip()

sv = Service(
    name = '完美配对',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助完美配对"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    



# 完美配对(Perfect Match)小游戏相关参数
ROW_NUM = 4
COL_NUM = 4
HIDDEN_NUM = 8
TURN_NUM = 3
BASIC_SHOW_TIME = 9
ANSWER_TIME = 15
TOTAL_PIC_NUM = ROW_NUM * COL_NUM
DB_PATH = os.path.expanduser("~/.hoshino/pcr_perfect_match.db")
assert HIDDEN_NUM * 2 <= TOTAL_PIC_NUM

gm = GameMaster(DB_PATH)


@sv.on_fullmatch(("完美配对排行", "完美配对排行榜", "完美配对群排行"))
async def perfect_match_group_ranking(bot, ev: CQEvent):
    ranking = gm.db.get_ranking(ev.group_id)
    msg = ["【完美配对小游戏排行榜】"]
    for i, item in enumerate(ranking):
        uid, score = item
        m = await bot.get_group_member_info(self_id=ev.self_id, group_id=ev.group_id, user_id=uid)
        name = m["card"] or m["nickname"] or str(uid)
        msg.append(f"第{i + 1}名: {name}, 总分: {score}分")
    await bot.send(ev, "\n".join(msg))


@sv.on_fullmatch('完美配对')
async def perfect_match(bot, ev: CQEvent):
    if gm.is_playing(ev.group_id):
        await bot.finish(ev, "游戏仍在进行中…")
    with gm.start_game(ev.group_id) as game:
        chosen_ids = random.sample(game_util.VALID_IDS, TOTAL_PIC_NUM)
        pushed_index = set()
        # 发送若干轮的隐藏部分子图的合成图，保证所有子图至少都被发送一次。发送完毕后等待若干秒再撤回图片
        for i in range(TURN_NUM):
            await bot.send(ev, f'记忆阶段{i+1}/{TURN_NUM}: ({BASIC_SHOW_TIME - i * 2}s后我会撤回图片哦~)')
            if i < TURN_NUM-1:
                shown_index = random.sample(range(TOTAL_PIC_NUM), TOTAL_PIC_NUM - HIDDEN_NUM)
                ids = [chosen_ids[i] if i in shown_index else game_util.UNKNOWN_ID for i in range(TOTAL_PIC_NUM)]
                pushed_index = pushed_index.union(set(shown_index))
            else:
                remnant_index = set(range(TOTAL_PIC_NUM)) - pushed_index
                shown_index = list(remnant_index)
                shown_index.extend(random.sample(pushed_index, TOTAL_PIC_NUM - HIDDEN_NUM - len(remnant_index)))
                ids = [chosen_ids[i] if i in shown_index else game_util.UNKNOWN_ID for i in range(TOTAL_PIC_NUM)]
            pic = MessageSegment.image(util.pic2b64(game_util.generate_full_pic(ROW_NUM, COL_NUM, ids)))
            msg = await bot.send(ev, pic)
            await asyncio.sleep(BASIC_SHOW_TIME - i * 2)
            await bot.delete_msg(message_id=msg['message_id'])
            await asyncio.sleep(3)
        # 开始答题
        correct_index = random.randint(0, TOTAL_PIC_NUM - 1)
        correct_id = chosen_ids[correct_index]
        game.answer = correct_index + 1
        correct_pic_img = MessageSegment.image(util.pic2b64(game_util.get_sub_pic_from_id(correct_id)))
        answer_number_img = MessageSegment.image(f'file:///{os.path.abspath(game_util.BACKGROUND_PIC_PATH)}')
        await bot.send(ev, f'还记得"{game_util.EXPLANATION[correct_id]}"的位置吗？{correct_pic_img}请告诉我它的编号~ ({ANSWER_TIME}s后公布答案){answer_number_img}')
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