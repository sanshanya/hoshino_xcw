import math, random, base64
from PIL import Image, ImageFont, ImageDraw

import hoshino
from hoshino import Service, util
from hoshino.modules.priconne import chara
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from . import *
from ...util import DailyNumberLimiter, FreqLimiter
from io import BytesIO


__BASE = os.path.split(os.path.realpath(__file__))
FRAME_DIR_PATH = os.path.join(__BASE[0],'image')
DIR_PATH = os.path.join(os.path.expanduser(hoshino.config.RES_DIR), 'img', 'priconne', 'unit')
DB_PATH = os.path.expanduser("~/.hoshino/poke_man_pcr.db")
SUPER_RARE_PROBABILITY = 0.08   # 戳一戳获得超稀有卡片的概率
RARE_PROBABILITY = 0.30         # 戳一戳获得稀有卡片的概率
REQUEST_VALID_TIME = 60         # 换卡请求的等待时间
POKE_COOLING_TIME = 3           # 增加冷却时间避免连续点击
POKE_DAILY_LIMIT = 1            # 每人每天最多戳机器人的次数，超过后机器人不再给卡，只回戳
GIVE_DAILY_LIMIT = 3            # 每人每天最多接受几次赠卡
COL_NUM = 17                    # 查看仓库时每行显示的卡片个数
BLACKLIST_CARD = []             # 填写不希望被加载的卡片文件名，以逗号分隔。如['icon_unit_100161.png'], 表示不加载六星猫拳的头像
# 献祭卡片时的获得不同稀有度卡片的概率，-1,0,1表示被献祭卡片的三种稀有度，后面长度为3的列表表示献祭获得卡片三种不同稀有度的概率，要求加和为1
MIX_PROBABILITY = {str(list((-1,-1))):[0.8,0.195,0.005], str(list((-1,0))):[0.49,0.5,0.01], str(list((-1,1))):[0.5,0.25,0.25],
                   str(list((0,0))):[0,0.92,0.08],       str(list((0,1))):[0,0.5,0.5],      str(list((1,1))):[0,0,1]}

PRELOAD=True                    # 是否启动时直接将所有图片加载到内存中以提高查看仓库的速度(增加约几M内存消耗)

sv = Service('poke-man-pcr', bundle='pcr娱乐', help_='''
戳一戳机器人, 她可能会送你公主连结卡片哦~
查看仓库 [@某人](这是可选参数): 查看某人的卡片仓库和收集度排名，不加参数默认查看自己的仓库
献祭 [卡片1昵称] [卡片2昵称]: 献祭两张卡片以获得一张新的卡片
赠送 [@某人] [赠送的卡片名]: 将自己的卡片赠予别人
交换 [卡片1昵称] [@某人] [卡片2昵称]: 向某人发起卡片交换请求，用自己的卡片1交换他的卡片2
确认交换: 收到换卡请求后一定时间内输入这个指令可完成换卡
'''.strip())
daily_limiter = DailyNumberLimiter(POKE_DAILY_LIMIT)
daily_give_limiter = DailyNumberLimiter(GIVE_DAILY_LIMIT)
cooling_time_limiter = FreqLimiter(POKE_COOLING_TIME)
exchange_request_master = ExchangeRequestMaster(REQUEST_VALID_TIME)
db = CardRecordDAO(DB_PATH)
font = ImageFont.truetype('arial.ttf', 16)
card_file_names_all = []
cards = {'1':[], '3':[], '6':[]}              # 1,3,6表示不同稀有度
chara_ids = {'1':[], '3':[], '6':[]}

# 资源预检
image_cache = {}
image_list = os.listdir(DIR_PATH)
for image in image_list:
    if not image.startswith('icon_unit_') or image in BLACKLIST_CARD:
        continue
    # 图像缓存
    if PRELOAD:
        image_path = os.path.join(DIR_PATH, image)
        image_cache[image] = Image.open(image_path)
    chara_id = int(image[10:14])
    if chara_id == 1000:
        continue
    rarity = image[14]
    cards[rarity].append(image)
    chara_ids[rarity].append(chara_id)
    card_file_names_all.append(image)
# 边框缓存
frame_names = ['superrare.png', 'rare.png', 'normal.png']
frames = {}
frames_aplha = {}
for frame_name in frame_names:
    frame = Image.open(FRAME_DIR_PATH + f'/{frame_name}')
    frame = frame.resize((80, 80), Image.ANTIALIAS)
    r,g,b,a = frame.split()
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
    return draw_num_text(add_rarity_frame(img, rarity), card_num)


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
    img.paste(frames[frame_file_name], (0,0), mask=frames_aplha[frame_file_name])
    return img


def draw_num_text(img, num):
    draw = ImageDraw.Draw(img)
    n = num if num < 100 else num
    text = f'x{n}'
    if len(text) == 2:
        offset_r = 0
        offset_t = 0
    else:
        offset_r = 10
        offset_t = 9
    draw.rectangle((59 - offset_r, 60, 75, 77), fill=(255, 255, 255))
    draw.rectangle((59 - offset_r, 60, 77, 75), fill=(255, 255, 255))
    draw.text((60-offset_t, 60), text, fill=(0, 0, 0), font=font)
    return img


def get_random_cards_list():
    r = random.random()
    if r < SUPER_RARE_PROBABILITY:
        cards_list = cards['6']
    elif r < SUPER_RARE_PROBABILITY + RARE_PROBABILITY:
        cards_list = cards['3']
    else:
        cards_list = cards['1']
    return cards_list


def get_random_cards(card_file_names_list = card_file_names_all, amount = 1):
    card_ids = []
    size = 80
    margin = 5
    col_num = math.ceil(amount/2)
    row_num = 2 if amount != 1 else 1
    base = Image.new('RGBA', (col_num * size + (col_num-1) * margin, (row_num * size + (row_num-1) * margin)), (255, 255, 255, 255))
    rarity_counter = {-1:0, 0:0, 1:0}
    for i in range(amount):
        random_card = random.choice(card_file_names_list) if card_file_names_list != card_file_names_all else random.choice(get_random_cards_list())
        card_id, rarity = get_card_id_by_file_name(random_card)
        card_ids.append(card_id)
        rarity_counter[rarity] += 1
        if PRELOAD:
            img = image_cache[random_card]
        else:
            img = Image.open(DIR_PATH + f'/{random_card}')
        row_index = i // col_num
        col_index = i % col_num
        img = img.resize((size, size), Image.ANTIALIAS)
        base.paste(add_rarity_frame(img, rarity), (col_index * (size + margin), row_index * (size + margin)))
    return card_ids, rarity_counter, MessageSegment.image(util.pic2b64(base))


# 输入'[稀有度前缀][角色昵称]'格式的卡片名, 例如'黑猫','稀有黑猫','超稀有黑猫', 输出角色昵称标准化后的结果如'「凯露」','稀有「凯露」','超稀有「凯露」'
def get_card_name_with_rarity(card_name):
    if card_name.startswith('超稀有'):
        chara_suffix = card_name[0:2]
        chara_nickname = card_name[3:]
    elif card_name.startswith('稀有'):
        chara_suffix = card_name[0:1]
        chara_nickname = card_name[2:]
    else:
        chara_suffix = ''
        chara_nickname = card_name
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
        chara_name_no_prefix = card_name[2:] if card_name.startswith('普通') else card_name
    chara_id = chara.name2id(chara_name_no_prefix)
    return (30000 + rarity * 1000 + chara_id) if chara_id != chara.UNKNOWN and chara_id in chara_ids[star] else 0
 
 
# 单次戳机器人获得的卡片数量
def roll_card_amount():
    roll = random.random()
    if roll <= 0.01:
        CARDS_EVERY_POKE = 10   #大暴击！
    elif 0.01 < roll <= 0.1:
        CARDS_EVERY_POKE = 5
    elif 0.1 < roll <= 0.3:
        CARDS_EVERY_POKE = 4
    elif 0.3 < roll <= 0.7:
        CARDS_EVERY_POKE = 3
    elif 0.7 < roll <= 0.9:
        CARDS_EVERY_POKE = 2
    else:
        CARDS_EVERY_POKE = 1
    return CARDS_EVERY_POKE


def get_card_id_by_file_name(image_file_name):
    chara_id = int(image_file_name[10:14])
    star = image_file_name[14]
    if star == '6':
        rarity = 1
    elif star == '3':
        rarity = 0
    else:
        rarity = -1
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
    if not cooling_time_limiter.check(uid):
        return
    cooling_time_limiter.start_cd(uid)
    if session.ctx['target_id'] != session.event.self_id:
        return
    if not daily_limiter.check((session.ctx['group_id'], session.ctx['user_id'])) or random.random() < 0.33:
        poke = MessageSegment(type_='poke',
                              data={
                                  'qq': str(session.ctx['user_id']),
                              })
        await session.send(poke)
    else:
        card_ids, rarity_counter, card = get_random_cards(card_file_names_all, roll_card_amount())
        at_user = MessageSegment.at(session.ctx['user_id'])
        dash =  '----------------------------------------'
        msg_part1 = f'\n超稀有x{rarity_counter[1]}' if rarity_counter[1] else ''
        msg_part2 = f'\n稀有卡x{rarity_counter[0]}' if rarity_counter[0] else ''
        msg_part3 = f'\n普通卡x{rarity_counter[-1]}' if rarity_counter[-1] else ''
        await session.send(f'别戳了别戳了o(╥﹏╥)o{card}{at_user}这些卡送给你了, 让我安静会...\n{dash}\n获得了:{msg_part1}{msg_part2}{msg_part3}')
        for card_id in card_ids:
            db.add_card_num(session.ctx['group_id'], session.ctx['user_id'], card_id)
        daily_limiter.increase((session.ctx['group_id'], session.ctx['user_id']))


@sv.on_prefix('献祭')
async def mix_card(bot, ev: CQEvent):
    # 参数识别
    s = ev.message.extract_plain_text()
    args = s.split(' ')
    if len(args) != 2:
        await bot.finish(ev, '请输入想要献祭的两张卡, 以空格分隔')
    card1_id = get_card_id_by_card_name(args[0])
    card2_id = get_card_id_by_card_name(args[1])
    if not card1_id:
        await bot.finish(ev, f'错误: 无法识别{args[0]}, 若为稀有或超稀有卡请在前面加上"稀有"或"超稀有"几个字')
    if not card2_id:
        await bot.finish(ev, f'错误: 无法识别{args[1]}, 若为稀有或超稀有卡请在前面加上"稀有"或"超稀有"几个字')
    card1_num = db.get_card_num(ev.group_id, ev.user_id, card1_id)
    card2_num = db.get_card_num(ev.group_id, ev.user_id, card2_id)
    if card1_id == card2_id:
        if card1_num < 2:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[0])}卡数量不足, 无法献祭')
    else:
        if card1_num == 0:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[0])}卡数量不足, 无法献祭')
        if card2_num == 0:
            await bot.finish(ev, f'{get_card_name_with_rarity(args[1])}卡数量不足, 无法献祭')
    # 开始献祭
    [normal_prob, rare_prob, super_rare_prob] = MIX_PROBABILITY[str(sorted(list((get_card_rarity(card1_id), get_card_rarity(card2_id)))))]
    r = random.random()
    if r < normal_prob:
        cards_list = cards['1']
    elif r < normal_prob + rare_prob:
        cards_list = cards['3']
    else:
        cards_list = cards['6']
    card_ids, rarity_counter, card = get_random_cards(cards_list)
    rarity_desc, chara_name = get_chara_name(card_ids[0])
    db.add_card_num(ev.group_id, ev.user_id, card1_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card2_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card_ids[0])
    await bot.send(ev, f'献祭了两张卡..然后{card}获得了{rarity_desc}「{chara_name}」X1~', at_sender=True)


@sv.on_prefix('交换')
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
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card1_name)}, 若为稀有或超稀有卡请在前面加上"稀有"或"超稀有"几个字')
    if not card2_id:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card2_name)}, 若为稀有或超稀有卡请在前面加上"稀有"或"超稀有"几个字')
    card1_num = db.get_card_num(ev.group_id, ev.user_id, card1_id)
    card2_num = db.get_card_num(ev.group_id, target_uid, card2_id)
    if card1_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(ev.user_id)}的{get_card_name_with_rarity(card1_name)}卡数量不足, 无法交换')
    if card2_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(target_uid)}的{get_card_name_with_rarity(card2_name)}卡数量不足, 无法交换')
    # 发起交换请求
    if exchange_request_master.has_exchange_request_to_confirm(ev.group_id, target_uid):
        await bot.finish(ev, f'您发起交易的对象目前正与他人交易中, 请稍等~', at_sender=True)
    exchange_request_master.add_exchange_request(ev.group_id, target_uid, ExchangeRequest(ev.user_id, card1_id, card1_name, target_uid, card2_id, card2_name))
    await bot.send(ev, f'{MessageSegment.at(target_uid)}\n叮~{MessageSegment.at(ev.user_id)}希望用他的{get_card_name_with_rarity(card1_name)}卡交换你的{get_card_name_with_rarity(card2_name)}卡，输入"确认交换"可完成交换({REQUEST_VALID_TIME}s后交换请求失效)')


@sv.on_fullmatch('确认交换')
async def confirm_exchange(bot, ev: CQEvent):
    if not exchange_request_master.has_exchange_request_to_confirm(ev.group_id, ev.user_id):
        await bot.finish(ev, '您还没有收到换卡请求~', at_sender=True)
    exchange_request = exchange_request_master.get_exchange_request(ev.group_id, ev.user_id)
    exchange_request_master.delete_exchange_request(ev.group_id, ev.user_id)
    card1_num = db.get_card_num(ev.group_id, exchange_request.sender_uid, exchange_request.card1_id)
    card2_num = db.get_card_num(ev.group_id, exchange_request.target_uid, exchange_request.card2_id)
    if card1_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(exchange_request.sender_uid)}的{get_card_name_with_rarity(exchange_request.card1_name)}卡数量不足, 无法交换')
    if card2_num == 0:
        await bot.finish(ev, f'{MessageSegment.at(exchange_request.target_uid)}的{get_card_name_with_rarity(exchange_request.card2_name)}卡数量不足, 无法交换')
    db.add_card_num(ev.group_id, exchange_request.sender_uid, exchange_request.card1_id, -1)
    db.add_card_num(ev.group_id, exchange_request.target_uid, exchange_request.card2_id, -1)
    db.add_card_num(ev.group_id, exchange_request.sender_uid, exchange_request.card2_id)
    db.add_card_num(ev.group_id, exchange_request.target_uid, exchange_request.card1_id)
    await bot.send(ev, '交换成功!')


@sv.on_prefix('赠送')
async def give(bot, ev:CQEvent):
    if len(ev.message) != 2 or ev.message[0].type != 'at' or ev.message[1].type != 'text':
        await bot.finish(ev, '参数格式错误, 请重试')
    target_uid = int(ev.message[0].data['qq'])
    if not daily_limiter.check((ev.group_id, target_uid)):
        await bot.finish(ev, f'{MessageSegment.at(target_uid)}今日接受赠送的次数已达上限，请明日再赠~')
    if target_uid == ev.user_id:
        await bot.finish(ev, '不用给自己赠卡~')
    card_name = ev.message[1].data['text'].strip()
    card_id = get_card_id_by_card_name(card_name)
    if not card_id:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card_name)}, 若为稀有或超稀有卡请在前面加上"稀有"或"超稀有"几个字')
    card_num = db.get_card_num(ev.group_id, ev.user_id, card_id)
    if card_num < 1:
        await bot.finish(ev, f'{get_card_name_with_rarity(card_name)}卡数量不足, 无法赠送')
    db.add_card_num(ev.group_id, ev.user_id, card_id, -1)
    db.add_card_num(ev.group_id, target_uid, card_id)
    daily_give_limiter.increase((ev.group_id, target_uid))
    await bot.send(ev, '赠送成功!')


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
    base = base.resize((40+COL_NUM*80+(COL_NUM-1)*10, 120+row_num*80+(row_num-1)*10), Image.ANTIALIAS)
    cards_num = db.get_cards_num(ev.group_id, uid)
    row_index_offset = 0
    row_offset = 0
    for star in cards.keys():
        cards_list = cards[star]
        for index, id in enumerate(cards_list):
            row_index = index // COL_NUM + row_index_offset
            col_index = index % COL_NUM
            card_id, rarity = get_card_id_by_file_name(cards_list[index])
            pic_path = DIR_PATH + f'/{cards_list[index]}'
            f = get_pic(pic_path, cards_num[card_id], rarity) if card_id in cards_num else get_grey_pic(pic_path, rarity)
            base.paste(f, (30 + col_index * 80 + (col_index - 1) * 10, row_offset + 40 + row_index * 80 + (row_index - 1) * 10))
        row_index_offset += row_nums[star]
        row_offset += 30
    ranking = db.get_group_ranking(ev.group_id, uid)
    ranking_desc = f'#{ranking}' if ranking != -1 else '未上榜'
    total_card_num = sum(cards_num.values())
    super_rare_card_num = len([card_id for card_id in cards_num if get_card_rarity(card_id) == 1])
    super_rare_card_total = len(cards['6'])
    rare_card_num = len([card_id for card_id in cards_num if get_card_rarity(card_id) == 0])
    rare_card_total = len(cards['3'])
    normal_card_num = len(cards_num) - super_rare_card_num - rare_card_num
    normal_card_total = len(cards['1'])
    buf = BytesIO()
    base = base.convert('RGB')
    base.save(buf,format='JPEG')
    base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    await bot.send(ev, f'{MessageSegment.at(uid)}的仓库:[CQ:image,file={base64_str}]\n持有卡片数: {total_card_num}\n普通卡收集: {normalize_digit_format(normal_card_num)}/{normalize_digit_format(normal_card_total)}\n稀有卡收集: {normalize_digit_format(rare_card_num)}/{normalize_digit_format(rare_card_total)}\n超稀有收集: {normalize_digit_format(super_rare_card_num)}/{normalize_digit_format(super_rare_card_total)}\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(card_file_names_all))}\n当前群排名: {ranking_desc}')
