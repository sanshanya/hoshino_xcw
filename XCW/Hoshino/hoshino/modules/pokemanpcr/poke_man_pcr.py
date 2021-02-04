import math
import random
import base64
from PIL import Image, ImageFont, ImageDraw

import hoshino
from hoshino import Service, priv, util
from hoshino.modules.priconne import chara, _pcr_data
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from . import *
from ...util import FreqLimiter
from io import BytesIO


__BASE = os.path.split(os.path.realpath(__file__))
FRAME_DIR_PATH = os.path.join(__BASE[0], 'image')
DIR_PATH = os.path.join(os.path.expanduser(
    hoshino.config.RES_DIR), 'img', 'priconne', 'unit')
DB_PATH = os.path.expanduser("~/.hoshino/poke_man_pcr.db")
POKE_GET_CARDS = 0.9           # 每一戳的卡片掉落几率
POKE_DAILY_LIMIT = 3           # 机器人每天掉落卡片的次数
RARE_PROBABILITY = 0.17         # 戳一戳获得稀有卡片的概率
SUPER_RARE_PROBABILITY = 0.03   # 戳一戳获得超稀有卡片的概率
REQUEST_VALID_TIME = 60         # 换卡请求的等待时间
POKE_TIP_LIMIT = 1              # 到达每日掉落上限后的短时最多提示次数
TIP_CD_LIMIT = 10*60            # 每日掉落上限提示冷却时间
POKE_COOLING_TIME = 3           # 增加冷却时间避免连续点击
GIVE_DAILY_LIMIT = 30            # 每人每天最多接受几次赠卡
RESET_HOUR = 0                  # 每日戳一戳、赠送等指令使用次数的重置时间，0代表凌晨0点，1代表凌晨1点，以此类推
COL_NUM = 17                    # 查看仓库时每行显示的卡片个数
OMIT_THRESHOLD = 15             # 当获得卡片数超过这个阈值时，不再显示获得卡片的具体名称，只显示获得的各个稀有度的卡片数目
# 填写不希望被加载的卡片文件名，以逗号分隔。如['icon_unit_100161.png'], 表示不加载六星猫拳的头像
BLACKLIST_CARD = ['icon_unit_100031.png']
# 献祭卡片时的获得不同稀有度卡片的概率，-1,0,1表示被献祭卡片的三种稀有度，后面长度为3的列表表示献祭获得卡片三种不同稀有度的概率，要求加和为1
MIX_PROBABILITY = {str(list((-1, -1))): [0.8, 0.194, 0.006], str(list((-1, 0))): [0.44, 0.5, 0.06], str(list((-1, 1))): [0.55, 0.3, 0.1],
                   str(list((0, 0))): [0.1, 0.8, 0.1],       str(list((0, 1))): [0.3, 0.5, 0.2],      str(list((1, 1))): [0.15, 0.25, 0.6]}
# 一键合成概率
OK_MIX_PROBABILITY = {str(list((-1, -1))): [0.846, 0.15, 0.004], str(list((-1, 0))): [0.56, 0.4, 0.04], str(list((-1, 1))): [0.68, 0.24, 0.08],
                      str(list((0, 0))): [0.33, 0.6, 0.07],       str(list((0, 1))): [0.44, 0.4, 0.16],      str(list((1, 1))): [0.2, 0.3, 0.5]}

PRELOAD = True                    # 是否启动时直接将所有图片加载到内存中以提高查看仓库的速度(增加约几M内存消耗)

sv_help = '''
戳一戳机器人, 她可能会送你公主连结卡片哦~
查看仓库 [@某人](这是可选参数): 不加参数默认查看自己的仓库
合成 [卡片1昵称] [卡片2昵称]: 献祭两张卡片以获得一张新的卡片
一键合成 [稀有度1] [稀有度2] [合成轮数](这是可选参数,不填则合成尽可能多的轮数): 一键进行若干轮"稀有度1"和"稀有度2"的卡片合成。注意: 使用一键合成指令获得稀有或超稀有卡的几率略低于使用合成指令
赠送 [@某人] [赠送的卡片名]: 将自己的卡片赠予别人
交换 [卡片1昵称] [@某人] [卡片2昵称]: 向某人发起卡片交换请求，用自己的卡片1交换他的卡片2
确认交换: 收到换卡请求后一定时间内输入这个指令可完成换卡
'''.strip()

sv = Service(
    name = '戳一戳',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '查询', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助戳一戳"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

poke_tip_cd_limiter = FreqLimiter(TIP_CD_LIMIT)
daily_tip_limiter = DailyAmountLimiter("tip",POKE_TIP_LIMIT, RESET_HOUR)
daily_limiter = DailyAmountLimiter("poke",POKE_DAILY_LIMIT, RESET_HOUR)
daily_give_limiter = DailyAmountLimiter("give",GIVE_DAILY_LIMIT, RESET_HOUR)
cooling_time_limiter = FreqLimiter(POKE_COOLING_TIME)
exchange_request_master = ExchangeRequestMaster(REQUEST_VALID_TIME)
db = CardRecordDAO(DB_PATH)
font = ImageFont.truetype('arial.ttf', 16)
card_ids = []
card_file_names_all = []
star2rarity = {'1': -1, '3': 0, '6': 1}                    # 角色头像星级->卡片稀有度
rarity_desc2rarity = {'普通': -1, '稀有': 0, '超稀有': 1}     # 稀有度文字描述->卡片稀有度
cards = {'1': [], '3': [], '6': []}                        # 1,3,6表示不同星级的角色头像
chara_ids = {'1': [], '3': [], '6': []}

# 资源预检
image_cache = {}
image_list = os.listdir(DIR_PATH)
for image in image_list:
    if not image.startswith('icon_unit_') or image in BLACKLIST_CARD:
        continue
    # 图像缓存
    if PRELOAD:
        image_path = os.path.join(DIR_PATH, image)
        img = Image.open(image_path)
        image_cache[image] = img.convert('RGBA') if img.mode != 'RGBA' else img
    chara_id = int(image[10:14])
    if chara_id == 1000 or chara_id not in _pcr_data.CHARA_NAME:
        continue
    star = image[14]
    if star not in star2rarity or image[15] != '1':
        continue
    cards[star].append(image)
    chara_ids[star].append(chara_id)
    card_ids.append(30000 + star2rarity[star] * 1000 + chara_id)
    card_file_names_all.append(image)
# 边框缓存
frame_names = ['superrare.png', 'rare.png', 'normal.png']
frames = {}
frames_aplha = {}
for frame_name in frame_names:
    frame = Image.open(FRAME_DIR_PATH + f'/{frame_name}')
    frame = frame.resize((80, 80), Image.ANTIALIAS)
    r, g, b, a = frame.split()
    frames[frame_name] = frame
    frames_aplha[frame_name] = a


def get_pic(pic_path, card_num, rarity):
    if PRELOAD:
        # 拆分路径和文件名
        pic_name = os.path.split(pic_path)[1]
        img = image_cache[pic_name]
    else:
        img = Image.open(pic_path)
    img = img.resize((80, 80), Image.ANTIALIAS)
    return draw_num_text(add_rarity_frame(img, rarity), card_num, True, (0, 0, 0), 0, 0)


def get_grey_pic(pic_path, rarity):
    if PRELOAD:
        # 拆分路径和文件名
        pic_name = os.path.split(pic_path)[1]
        img = image_cache[pic_name]
    else:
        img = Image.open(pic_path)
    img = img.resize((80, 80), Image.ANTIALIAS)
    img = add_rarity_frame(img, rarity)
    img = img.convert('L')
    return img


def add_rarity_frame(img, rarity):
    if rarity == 1:
        frame_file_name = frame_names[0]
    elif rarity == 0:
        frame_file_name = frame_names[1]
    else:
        frame_file_name = frame_names[2]
    img.paste(frames[frame_file_name], (0, 0),
              mask=frames_aplha[frame_file_name])
    return img


def add_card_amount(img, card_amount):
    quantity_base = Image.open(FRAME_DIR_PATH + '/quantity.png')
    img.paste(quantity_base, (53, 54), mask=quantity_base.split()[3])
    return draw_num_text(img, card_amount, False, (255, 255, 255), 2, 1)


def add_icon(base, icon_name, x, y):
    icon = Image.open(FRAME_DIR_PATH + f'/{icon_name}')
    base.paste(icon, (x, y), mask=icon.split()[3])
    return base


def draw_num_text(img, num, draw_base_color, color, offset_x, offset_y):
    draw = ImageDraw.Draw(img)
    n = num if num < 100 else num
    text = f'×{n}'
    if len(text) == 2:
        offset_r = 0
        offset_t = 0
    else:
        offset_r = 10
        offset_t = 9
    if draw_base_color:
        draw.rectangle((59 - offset_r, 60, 75, 77), fill=(255, 255, 255))
        draw.rectangle((59 - offset_r, 60, 77, 75), fill=(255, 255, 255))
    draw.text((60-offset_t+offset_x, 60+offset_y), text, fill=color, font=font)
    return img


def get_random_cards_list(super_rare_prob, rare_prob):
    r = random.random()
    if r < super_rare_prob:
        cards_list = cards['6']
    elif r < super_rare_prob + rare_prob:
        cards_list = cards['3']
    else:
        cards_list = cards['1']
    return cards_list


def get_random_cards(origin_cards, row_num, col_num, amount, bonus, get_random_cards_func=get_random_cards_list, *args):
    size = 80
    margin = 7
    margin_offset_x = 6
    margin_offset_y = 6
    cards_amount = []
    extra_bonus = False
    for i in range(amount):
        a = roll_extra_bonus() if bonus else 1
        cards_amount.append(a)
        if a != 1:
            extra_bonus = True
    offset_y = 18 if extra_bonus else 0
    offset_critical_strike = 7 if extra_bonus else 0
    size_x, size_y = (col_num * size + (col_num+1) * margin + 2 * margin_offset_x, offset_y +
                      row_num * size + (row_num+1) * margin + 2 * margin_offset_y + offset_critical_strike)
    base = Image.new('RGBA', (size_x, size_y), (255, 255, 255, 255))
    frame = Image.open(FRAME_DIR_PATH + '/background.png')
    frame = frame.resize((size_x, size_y - offset_y), Image.ANTIALIAS)
    base.paste(frame, (0, offset_y), mask=frame.split()[3])
    if extra_bonus:
        base = add_icon(base, 'pokecriticalstrike.png',
                        int(size_x/2) - 71, int(offset_y/2) - 2)
    card_counter = {}
    rarity_counter = {1: [0, 0], 0: [0, 0], -1: [0, 0]}
    card_descs = []
    rarity_desc = {1: '超稀有', 0: '稀有', -1: '普通'}
    for i in range(amount):
        random_card = random.choice(get_random_cards_func(*args))
        card_id, rarity = get_card_id_by_file_name(random_card)
        new_string = ' 【NEW】' if card_id not in origin_cards and card_id not in card_counter else ''
        card_amount = cards_amount[i]
        card_counter[card_id] = card_amount if card_id not in card_counter else card_counter[card_id] + card_amount
        card_desc = f'{rarity_desc[rarity]}「{get_chara_name(card_id)[1]}」×{card_amount}{new_string}'
        card_descs.append(card_desc)
        rarity_counter[rarity][0] += 1
        rarity_counter[rarity][1] += 1 if new_string else 0
        if PRELOAD:
            img = image_cache[random_card]
        else:
            img = Image.open(DIR_PATH + f'/{random_card}')
            img = img.convert('RGBA') if img.mode != 'RGBA' else img
        row_index = i // col_num
        col_index = i % col_num
        img = img.resize((size, size), Image.ANTIALIAS)
        img = add_rarity_frame(img, rarity)
        if card_amount > 1:
            img = add_card_amount(img, card_amount)
        coor_x, coor_y = (margin + margin_offset_x + col_index * (size + margin), margin +
                          margin_offset_y + offset_y + offset_critical_strike + row_index * (size + margin))
        base.paste(img, (coor_x, coor_y), mask=img.split()[3])
        if card_id not in origin_cards:
            base = add_icon(base, 'new.png', coor_x + size - 27, coor_y - 5)
    # 当获得的卡片数过多时，只显示各稀有度获得的卡片数量
    if amount > OMIT_THRESHOLD:
        card_descs = []
        rarity_desc = {1: '超稀有', 0: '稀有卡', -1: '普通卡'}
        for rarity in rarity_counter:
            if rarity_counter[rarity][0] > 0:
                msg_part = f' (【NEW】x{rarity_counter[rarity][1]})' if rarity_counter[rarity][1] else ''
                card_descs.append(
                    f'【{rarity_desc[rarity]}】x{rarity_counter[rarity][0]}{msg_part}')
    return card_counter, card_descs, MessageSegment.image(util.pic2b64(base))


# 输入'[稀有度前缀][角色昵称]'格式的卡片名, 例如'黑猫','稀有黑猫','超稀有黑猫', 输出角色昵称标准化后的结果如'「凯露」','稀有「凯露」','超稀有「凯露」'
def get_card_name_with_rarity(card_name):
    if card_name.startswith('超稀有'):
        chara_suffix = card_name[0:3]
        chara_nickname = card_name[3:]
    elif card_name.startswith('稀有'):
        chara_suffix = card_name[0:2]
        chara_nickname = card_name[2:]
    else:
        chara_suffix = '普通'
        chara_nickname = card_name[2:] if card_name.startswith(
            '普通') else card_name
    chara_name = chara.fromname(chara_nickname).name
    return f'{chara_suffix}「{chara_name}」'


# 由卡片id(形如3xxxx)提取稀有度前缀和角色名
def get_chara_name(card_id):
    chara_id = card_id % 10000
    if 3000 > chara_id > 2000:
        chara_id -= 1000
        rarity_desc = '【超稀有】的'
    elif 2000 > chara_id > 1000 or chara_id > 3000:
        rarity_desc = '【稀有】的'
    else:
        chara_id += 1000
        rarity_desc = '【普通】的'
    return rarity_desc, chara.fromid(chara_id).name


# 由'[稀有度前缀][角色昵称]'格式的卡片名, 返回卡片id(形如3xxxx)，如果卡片不存在则返回0
def get_card_id_by_card_name(card_name):
    if card_name.startswith('超稀有'):
        rarity = 1
        star = '6'
        chara_name_no_prefix = card_name[3:]
    elif card_name.startswith('稀有'):
        rarity = 0
        star = '3'
        chara_name_no_prefix = card_name[2:]
    else:
        rarity = -1
        star = '1'
        chara_name_no_prefix = card_name[2:] if card_name.startswith(
            '普通') else card_name
    chara_id = chara.name2id(chara_name_no_prefix)
    return (30000 + rarity * 1000 + chara_id) if chara_id != chara.UNKNOWN and chara_id in chara_ids[star] else 0


# 单次戳机器人获得的卡片数量
def roll_cards_amount():
    roll = random.random()
    if roll <= 0.01:
        CARDS_EVERY_POKE = 10  # 大暴击！
    elif 0.01 < roll <= 0.1:
        CARDS_EVERY_POKE = 5
    elif 0.1 < roll <= 0.3:
        CARDS_EVERY_POKE = 4
    elif 0.3 < roll <= 0.7:
        CARDS_EVERY_POKE = 3
    elif 0.7 < roll <= 0.9:
        CARDS_EVERY_POKE = 2
    else:
        CARDS_EVERY_POKE = 10
    return CARDS_EVERY_POKE


def roll_extra_bonus():
    roll = random.random()
    if roll < 0.01:
        amount = 4
    elif roll < 0.1:
        amount = 2
    else:
        amount = 1
    return amount


def get_card_id_by_file_name(image_file_name):
    chara_id = int(image_file_name[10:14])
    rarity = star2rarity[image_file_name[14]]
    return 30000 + rarity * 1000 + chara_id, rarity


def get_card_rarity(card_id):
    if 33000 > card_id > 32000:
        return 1
    elif card_id < 31000:
        return -1
    else:
        return 0


def normalize_digit_format(n):
    return f'0{n}' if n < 10 else f'{n}'


@sv.on_notice('notify.poke')
async def poke_back(session: NoticeSession):
    uid = session.ctx['user_id']
    at_user = MessageSegment.at(session.ctx['user_id'])
    guid = session.ctx['group_id'], session.ctx['user_id']
    if not cooling_time_limiter.check(uid):
        return
    cooling_time_limiter.start_cd(uid)
    if session.ctx['target_id'] != session.event.self_id:
        return
    if not daily_limiter.check(guid) and not daily_tip_limiter.check(guid):
        poke_tip_cd_limiter.start_cd(guid)
    if not daily_limiter.check(guid) and poke_tip_cd_limiter.check(guid):
        daily_tip_limiter.increase(guid)
        await session.send(f'{at_user}你今天戳得已经够多的啦，再戳也不会有奇怪的东西掉下来的~')
        return
    daily_tip_limiter.reset(guid)
    if not daily_limiter.check(guid) or random.random() > POKE_GET_CARDS:
        poke = MessageSegment(type_='poke',
                              data={
                                  'qq': str(session.ctx['user_id']),
                              })
        await session.send(poke)
    else:
        amount = roll_cards_amount()
        col_num = math.ceil(amount / 2)
        row_num = 2 if amount != 1 else 1
        card_counter, card_descs, card = get_random_cards(db.get_cards_num(session.ctx['group_id'], session.ctx['user_id']), row_num, col_num,
                                                          amount, True, get_random_cards_list, SUPER_RARE_PROBABILITY, RARE_PROBABILITY)
        dash = '----------------------------------------'
        msg_part = '\n'.join(card_descs)
        await session.send(f'别戳了别戳了o(╥﹏╥)o{card}{at_user}这些卡送给你了, 让我安静会...\n{dash}\n获得了:\n{msg_part}')
        for card_id in card_counter.keys():
            db.add_card_num(
                session.ctx['group_id'], session.ctx['user_id'], card_id, card_counter[card_id])
        daily_limiter.increase(guid)


@sv.on_prefix(('献祭', '合成', '融合'))
async def mix_card(bot, ev: CQEvent):
    # 参数识别
    s = ev.message.extract_plain_text()
    args = s.split(' ')
    if len(args) != 2:
        await bot.finish(ev, '请输入想要合成的两张卡, 以空格分隔')
    card1_id = get_card_id_by_card_name(args[0])
    card2_id = get_card_id_by_card_name(args[1])
    if not card1_id:
        await bot.finish(ev, f'错误: 无法识别{args[0]}, 若为稀有或超稀有卡请在名称前加上"稀有"或"超稀有"')
    if not card2_id:
        await bot.finish(ev, f'错误: 无法识别{args[1]}, 若为稀有或超稀有卡请在名称前加上"稀有"或"超稀有"')
    card1_num = db.get_card_num(ev.group_id, ev.user_id, card1_id)
    card2_num = db.get_card_num(ev.group_id, ev.user_id, card2_id)
    if card1_id == card2_id:
        if card1_num < 2:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[0])}卡数量不足, 无法合成')
    else:
        if card1_num == 0:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[0])}卡数量不足, 无法合成')
        if card2_num == 0:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[1])}卡数量不足, 无法合成')
    # 开始献祭
    [normal_prob, rare_prob, super_rare_prob] = MIX_PROBABILITY[str(
        sorted(list((get_card_rarity(card1_id), get_card_rarity(card2_id)))))]
    card_counter, card_descs, card = get_random_cards(db.get_cards_num(
        ev.group_id, ev.user_id), 1, 1, 1, False, get_random_cards_list, super_rare_prob, rare_prob)
    card_id = list(card_counter.keys())[0]
    rarity_desc, chara_name = get_chara_name(card_id)
    db.add_card_num(ev.group_id, ev.user_id, card1_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card2_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card_id)
    await bot.send(ev, f'将两张卡片进行了融合……然后{card}获得了{rarity_desc}「{chara_name}」×1~', at_sender=True)


@sv.on_prefix(('一键献祭', '一键合成', '一键融合', '全部献祭', '全部合成', '全部融合'))
async def auto_mix_card(bot, ev: CQEvent):
    # 参数识别
    s = ev.message.extract_plain_text()
    args = s.split(' ')
    if len(args) == 2 and args[0] in rarity_desc2rarity and args[1] in rarity_desc2rarity:
        pass
    elif len(args) == 3 and args[0] in rarity_desc2rarity and args[1] in rarity_desc2rarity and args[2].isdigit() and int(args[2]) > 0:
        pass
    else:
        await bot.finish(ev, '参数格式错误, 请按正确格式输入指令参数')
    # 自动消耗多余的卡
    surplus_cards = db.get_surplus_cards(ev.group_id, ev.user_id)
    surplus_cards = {card_id: card_amount for card_id,
                     card_amount in surplus_cards.items() if card_id in card_ids}
    if args[0] == args[1]:
        rarity = rarity_desc2rarity[args[0]]
        rarity1, rarity2 = rarity, rarity
        available_cards = {card_id: card_amount for card_id, card_amount in surplus_cards.items(
        ) if get_card_rarity(card_id) == rarity}
        available_card_amount = sum(available_cards.values())
        if len(args) == 3 and int(args[2])*2 > available_card_amount:
            await bot.finish(ev, f'合成失败, 多余的【{args[0]}】卡数量不足{args[2]*2}, 无法一键合成{args[2]}次.')
        if len(args) == 2 and available_card_amount < 2:
            await bot.finish(ev, f'合成失败, 多余的【{args[0]}】卡数量不足2, 无法一键合成')
        mix_rounds = int(args[2]) if len(
            args) == 3 else math.floor(available_card_amount/2)
        mixed_cards_amount = 0
        for card_id in available_cards:
            card_amount = available_cards[card_id]
            if mixed_cards_amount + card_amount <= 2 * mix_rounds:
                db.add_card_num(ev.group_id, ev.user_id, card_id, -card_amount)
                mixed_cards_amount += card_amount
            else:
                db.add_card_num(ev.group_id, ev.user_id,
                                card_id, -(2*mix_rounds - mixed_cards_amount))
                break
    else:
        rarity1 = rarity_desc2rarity[args[0]]
        rarity2 = rarity_desc2rarity[args[1]]
        available_cards1 = {card_id: card_amount for card_id, card_amount in surplus_cards.items(
        ) if get_card_rarity(card_id) == rarity1}
        available_cards2 = {card_id: card_amount for card_id, card_amount in surplus_cards.items(
        ) if get_card_rarity(card_id) == rarity2}
        available_card_amount1 = sum(available_cards1.values())
        available_card_amount2 = sum(available_cards2.values())
        if len(args) == 3:
            if int(args[2]) > available_card_amount1:
                await bot.finish(ev, f'合成失败, 多余的【{args[0]}】卡数量不足{args[2]}, 无法一键合成{args[2]}次.')
            if int(args[2]) > available_card_amount2:
                await bot.finish(ev, f'合成失败, 多余的【{args[1]}】卡数量不足{args[2]}, 无法一键合成{args[2]}次.')
        if len(args) == 2:
            if available_card_amount1 < 1:
                await bot.finish(ev, f'合成失败, 多余的【{args[0]}】卡数量不足1, 无法一键合成')
            if available_card_amount2 < 1:
                await bot.finish(ev, f'合成失败, 多余的【{args[1]}】卡数量不足1, 无法一键合成')
        mix_rounds = int(args[2]) if len(args) == 3 else min(
            available_card_amount1, available_card_amount2)
        for available_cards in [available_cards1, available_cards2]:
            mixed_cards_amount = 0
            for card_id in available_cards:
                card_amount = available_cards[card_id]
                if mixed_cards_amount + card_amount <= 2 * mix_rounds:
                    db.add_card_num(ev.group_id, ev.user_id,
                                    card_id, -card_amount)
                    mixed_cards_amount += card_amount
                else:
                    db.add_card_num(ev.group_id, ev.user_id,
                                    card_id, -(2*mix_rounds - mixed_cards_amount))
                    break
    # 获得自动合成的卡
    [normal_prob, rare_prob, super_rare_prob] = OK_MIX_PROBABILITY[str(
        sorted(list((rarity1, rarity2))))]
    col_num = math.ceil(math.sqrt(mix_rounds))
    row_num = math.ceil(mix_rounds / col_num)
    card_counter, card_descs, card = get_random_cards(db.get_cards_num(
        ev.group_id, ev.user_id), row_num, col_num, mix_rounds, False, get_random_cards_list, super_rare_prob, rare_prob)
    msg_part = '\n'.join(card_descs)
    await bot.send(ev, f'进行了{mix_rounds}轮融合……然后{card}获得了:\n{msg_part}', at_sender=True)
    for card_id in card_counter.keys():
        db.add_card_num(ev.group_id, ev.user_id,
                        card_id, card_counter[card_id])


@sv.on_prefix(('交换', '交易', '互换'))
async def exchange_cards(bot, ev: CQEvent):
    # 参数识别
    if len(ev.message) != 3:
        await bot.finish(ev, '参数格式错误, 请重试')
    if ev.message[0].type != 'text' or ev.message[1].type != 'at' or ev.message[2].type != 'text':
        await bot.finish(ev, '参数格式错误, 请重试')
    target_uid = int(ev.message[1].data['qq'])
    card1_name = ev.message[0].data['text'].strip()
    card2_name = ev.message[2].data['text'].strip()
    card1_id = get_card_id_by_card_name(card1_name)
    card2_id = get_card_id_by_card_name(card2_name)
    if not card1_id:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card1_name)}, 若为稀有或超稀有卡请在名称前加上"稀有"或"超稀有"')
    if not card2_id:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card2_name)}, 若为稀有或超稀有卡请在名称前加上"稀有"或"超稀有"')
    card1_num = db.get_card_num(ev.group_id, ev.user_id, card1_id)
    card2_num = db.get_card_num(ev.group_id, target_uid, card2_id)
    if card1_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(ev.user_id)}的{get_card_name_with_rarity(card1_name)}卡数量不足, 无法交换')
    if card2_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(target_uid)}的{get_card_name_with_rarity(card2_name)}卡数量不足, 无法交换')
    # 发起交换请求
    if exchange_request_master.has_exchange_request_to_confirm(ev.group_id, target_uid):
        await bot.finish(ev, '您发起交易的对象目前正与他人交易中, 请稍等~', at_sender=True)
    exchange_request_master.add_exchange_request(ev.group_id, target_uid, ExchangeRequest(
        ev.user_id, card1_id, card1_name, target_uid, card2_id, card2_name))
    await bot.send(ev, f'{MessageSegment.at(target_uid)}\n叮~{MessageSegment.at(ev.user_id)}希望用他的{get_card_name_with_rarity(card1_name)}卡交换你的{get_card_name_with_rarity(card2_name)}卡，输入"确认交换"可完成交换({REQUEST_VALID_TIME}s后交换请求失效)')


@sv.on_fullmatch(('确认交换', '同意交换'))
async def confirm_exchange(bot, ev: CQEvent):
    if not exchange_request_master.has_exchange_request_to_confirm(ev.group_id, ev.user_id):
        await bot.finish(ev, '您还没有收到换卡请求~', at_sender=True)
    exchange_request = exchange_request_master.get_exchange_request(
        ev.group_id, ev.user_id)
    exchange_request_master.delete_exchange_request(ev.group_id, ev.user_id)
    card1_num = db.get_card_num(
        ev.group_id, exchange_request.sender_uid, exchange_request.card1_id)
    card2_num = db.get_card_num(
        ev.group_id, exchange_request.target_uid, exchange_request.card2_id)
    if card1_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(exchange_request.sender_uid)}的{get_card_name_with_rarity(exchange_request.card1_name)}卡数量不足, 无法交换')
    if card2_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(exchange_request.target_uid)}的{get_card_name_with_rarity(exchange_request.card2_name)}卡数量不足, 无法交换')
    db.add_card_num(ev.group_id, exchange_request.sender_uid,
                    exchange_request.card1_id, -1)
    db.add_card_num(ev.group_id, exchange_request.target_uid,
                    exchange_request.card2_id, -1)
    db.add_card_num(ev.group_id, exchange_request.sender_uid,
                    exchange_request.card2_id)
    db.add_card_num(ev.group_id, exchange_request.target_uid,
                    exchange_request.card1_id)
    await bot.send(ev, '交换成功!')


@sv.on_prefix(('赠送', '白给', '白送'))
async def give(bot, ev: CQEvent):
    if len(ev.message) != 2 or ev.message[0].type != 'at' or ev.message[1].type != 'text':
        await bot.finish(ev, '参数格式错误, 请重试')
    target_uid = int(ev.message[0].data['qq'])
    if not daily_give_limiter.check((ev.group_id, target_uid)):
        await bot.finish(ev, f'{MessageSegment.at(target_uid)}的今日接受赠送次数已达上限，明天再送给TA吧~')
    if target_uid == ev.user_id:
        await bot.finish(ev, '不用给自己赠卡~')
    card_name = ev.message[1].data['text'].strip()
    card_id = get_card_id_by_card_name(card_name)
    if not card_id:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card_name)}, 若为稀有或超稀有卡请在名称前加上"稀有"或"超稀有"')
    card_num = db.get_card_num(ev.group_id, ev.user_id, card_id)
    if card_num < 1:
        await bot.finish(ev, f'{get_card_name_with_rarity(card_name)}卡数量不足, 无法赠送')
    db.add_card_num(ev.group_id, ev.user_id, card_id, -1)
    db.add_card_num(ev.group_id, target_uid, card_id)
    daily_give_limiter.increase((ev.group_id, target_uid))
    await bot.send(ev, f'{MessageSegment.at(ev.user_id)}将{get_card_name_with_rarity(card_name)}赠送给了{MessageSegment.at(target_uid)}')


@sv.on_prefix('查看仓库')
async def storage(bot, ev: CQEvent):
    if len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = ev.user_id
    elif ev.message[0].type == 'at':
        uid = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    row_nums = {}
    for star in cards.keys():
        row_nums[star] = math.ceil(len(cards[star]) / COL_NUM)
    row_num = sum(row_nums.values())
    base = Image.open(FRAME_DIR_PATH + '/frame.png')
    base = base.resize((40+COL_NUM*80+(COL_NUM-1)*10, 120 +
                        row_num*80+(row_num-1)*10), Image.ANTIALIAS)
    cards_num = db.get_cards_num(ev.group_id, uid)
    cards_num = {card_id: card_amount for card_id,
                 card_amount in cards_num.items() if card_id in card_ids}
    row_index_offset = 0
    row_offset = 0
    for star in cards.keys():
        cards_list = cards[star]
        for index, id in enumerate(cards_list):
            row_index = index // COL_NUM + row_index_offset
            col_index = index % COL_NUM
            card_id, rarity = get_card_id_by_file_name(cards_list[index])
            pic_path = DIR_PATH + f'/{cards_list[index]}'
            f = get_pic(pic_path, cards_num[card_id], rarity) if card_id in cards_num else get_grey_pic(
                pic_path, rarity)
            base.paste(f, (30 + col_index * 80 + (col_index - 1) * 10,
                           row_offset + 40 + row_index * 80 + (row_index - 1) * 10))
        row_index_offset += row_nums[star]
        row_offset += 30
    ranking = db.get_group_ranking(ev.group_id, uid)
    ranking_desc = f'第{ranking}位' if ranking != -1 else '未上榜'
    total_card_num = sum(cards_num.values())
    super_rare_card_num = len(
        [card_id for card_id in cards_num if get_card_rarity(card_id) == 1])
    super_rare_card_total = len(cards['6'])
    rare_card_num = len(
        [card_id for card_id in cards_num if get_card_rarity(card_id) == 0])
    rare_card_total = len(cards['3'])
    normal_card_num = len(cards_num) - super_rare_card_num - rare_card_num
    normal_card_total = len(cards['1'])
    buf = BytesIO()
    base = base.convert('RGB')
    base.save(buf, format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'{MessageSegment.at(uid)}的仓库:[CQ:image,file={base64_str}]\n持有卡片数: {total_card_num}\n普通卡收集: {normalize_digit_format(normal_card_num)}/{normalize_digit_format(normal_card_total)}\n稀有卡收集: {normalize_digit_format(rare_card_num)}/{normalize_digit_format(rare_card_total)}\n超稀有收集: {normalize_digit_format(super_rare_card_num)}/{normalize_digit_format(super_rare_card_total)}\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}')


# 当增加新角色后不重启hoshino刷新现有缓存
@sv.on_fullmatch('刷新卡片')
async def refresh_unit_cache(bot, event: CQEvent):
    cards['1'] = []
    cards['3'] = []
    cards['6'] = []

    chara_ids['1'] = []
    chara_ids['3'] = []
    chara_ids['6'] = []

    card_ids.clear()
    card_file_names_all.clear()
    image_list = os.listdir(DIR_PATH)
    for image in image_list:
        if not image.startswith('icon_unit_') or image in BLACKLIST_CARD:
            continue
        # 图像缓存
        if PRELOAD:
            image_path = os.path.join(DIR_PATH, image)
            img = Image.open(image_path)
            image_cache[image] = img.convert(
                'RGBA') if img.mode != 'RGBA' else img
        chara_id = int(image[10:14])
        if chara_id == 1000 or chara_id not in _pcr_data.CHARA_NAME:
            continue
        star = image[14]
        if star not in star2rarity or image[15] != '1':
            continue
        cards[star].append(image)
        chara_ids[star].append(chara_id)
        card_ids.append(30000 + star2rarity[star] * 1000 + chara_id)
        card_file_names_all.append(image)
    # 边框缓存
    for frame_name in frame_names:
        frame = Image.open(FRAME_DIR_PATH + f'/{frame_name}')
        frame = frame.resize((80, 80), Image.ANTIALIAS)
        r, g, b, a = frame.split()
        frames[frame_name] = frame
        frames_aplha[frame_name] = a
    await bot.send(event, '我好了')