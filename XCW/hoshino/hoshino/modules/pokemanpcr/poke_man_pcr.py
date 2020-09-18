import math, random
from PIL import Image, ImageFont, ImageDraw

from hoshino import Service, util
from hoshino.modules.priconne import chara
from hoshino.typing import MessageSegment, NoticeSession, CQEvent
from . import *
from ...util import DailyNumberLimiter


DIR_PATH = './hoshino/modules/pokemanpcr/image'
DB_PATH = os.path.expanduser("~/.hoshino/poke_man_pcr.db")
REQUEST_VALID_TIME = 60     # 换卡请求的等待时间
POKE_DAILY_LIMIT = 5        # 每人每天戳机器人获得卡片的数量上限
COL_NUM = 8                 # 查看仓库时每行显示的卡片个数


sv = Service('poke-man-pcr', bundle='pcr娱乐', help_='''
戳一戳机器人 她可能会送你公主连结卡片哦
[查看仓库] [@某人](这是可选参数) 查看某人的卡片仓库和收集度排名，不加参数默认查看自己的仓库
[献祭] [卡片1昵称] [卡片2昵称] 献祭两张卡片以获得一张新的卡片
[交换] [卡片1昵称] [@某人] [卡片2昵称] 向某人发起卡片交换请求，用自己的卡片1交换他的卡片2
[确认交换] 收到换卡请求后一定时间内输入这个指令可完成换卡
'''.strip())
daily_limiter = DailyNumberLimiter(POKE_DAILY_LIMIT)
exchange_request_master = ExchangeRequestMaster(REQUEST_VALID_TIME)
db = CardRecordDAO(DB_PATH)
font = ImageFont.truetype('arial.ttf', 16)
card_file_names_all = os.listdir(DIR_PATH)
card_file_names_all.remove('frame.png')
card_file_names_normal = [file_name for file_name in card_file_names_all if file_name.startswith('31')]
card_file_names_rare = [file_name for file_name in card_file_names_all if file_name.startswith('32')]
cards = [int(file_name.split('.')[0]) for file_name in card_file_names_all]


def get_pic(pic_path, card_num):
    img = Image.open(pic_path)
    img = img.resize((80, 80), Image.ANTIALIAS)
    return draw_num_text(img, card_num)


def get_grey_pic(pic_path):
    img = Image.open(pic_path).convert('L')
    img = img.resize((80, 80), Image.ANTIALIAS)
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


def get_random_card(card_file_names_list = card_file_names_all):
    random_card = random.choice(card_file_names_list)
    card_id = int(random_card.split('.')[0])
    im = Image.open(DIR_PATH + f'/{random_card}')
    im = im.resize((80, 80), Image.ANTIALIAS)
    return card_id, MessageSegment.image(util.pic2b64(im))


def get_card_name_with_rarity(string):
    rarity = 1 if string.startswith('稀有') else 0
    chara_nickname = string[2:] if rarity else string
    chara_name = chara.fromname(chara_nickname).name
    return f'稀有「{chara_name}」' if rarity else f'「{chara_name}」'


def get_chara_name(card_id):
    chara_id = card_id % 10000
    rarity = 1 if chara_id > 2000 else 0
    chara_id -= rarity * 1000
    return rarity, chara.fromid(chara_id).name


def get_card_id(chara_name):
    rarity = 1 if chara_name.startswith('稀有') else 0
    chara_name_no_prefix = chara_name[2:] if rarity else chara_name
    chara_id = chara.name2id(chara_name_no_prefix)
    return (30000 + rarity * 1000 + chara_id) if chara_id != chara.UNKNOWN else 0


def get_card_rarity(card_id):
    return 1 if card_id > 32000 else 0


def normalize_digit_format(n):
    return f'0{n}' if n < 10 else f'{n}'


@sv.on_notice('notify.poke')
async def poke_back(session: NoticeSession):
    if session.ctx['target_id'] != session.event.self_id:
        return
    if not daily_limiter.check((session.ctx['group_id'], session.ctx['user_id'])) or random.random() < 0.33:
        poke = MessageSegment(type_='poke',
                              data={
                                  'qq': str(session.ctx['user_id']),
                              })
        await session.send(poke)
    else:
        cards_list = card_file_names_rare if random.random() < 0.10 else card_file_names_normal
        card_id, card = get_random_card(cards_list)
        rarity, chara_name = get_chara_name(card_id)
        rarity_desc = '【稀有】的' if rarity == 1 else ''
        at_user = MessageSegment.at(session.ctx['user_id'])
        await session.send(f'别戳了别戳了o(╥﹏╥)o{card}{at_user}这张{rarity_desc}「{chara_name}」送给你了, 让我安静会...')
        db.add_card_num(session.ctx['group_id'], session.ctx['user_id'], card_id)
        daily_limiter.increase((session.ctx['group_id'], session.ctx['user_id']))


@sv.on_prefix('献祭')
async def mix_card(bot, ev: CQEvent):
    # 参数识别
    s = ev.message.extract_plain_text()
    args = s.split(' ')
    if len(args) != 2:
        await bot.finish(ev, '请输入想要献祭的两张卡, 以空格分隔')
    card1_id = get_card_id(args[0])
    card2_id = get_card_id(args[1])
    if not card1_id or card1_id not in cards:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(args[0])}, 若为稀有卡请在前面加上"稀有"二字')
    if not card2_id or card2_id not in cards:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(args[1])}, 若为稀有卡请在前面加上"稀有"二字')
    card1_num = db.get_card_num(ev.group_id, ev.user_id, card1_id)
    card2_num = db.get_card_num(ev.group_id, ev.user_id, card2_id)
    if card1_num == 0:
        await bot.finish(ev, f'{get_card_name_with_rarity(args[0])}卡数量不足, 无法献祭')
    if card2_num == 0:
        await bot.finish(ev, f'{get_card_name_with_rarity(args[1])}卡数量不足, 无法献祭')
    # 开始献祭
    total_rarity = get_card_rarity(card1_id) + get_card_rarity(card2_id)
    if total_rarity == 0:
        cards_list = card_file_names_rare if random.random() < 0.10 else card_file_names_normal
    elif total_rarity == 1:
        cards_list = card_file_names_rare if random.random() < 0.50 else card_file_names_normal
    else:
        cards_list = card_file_names_rare
    card_id, card = get_random_card(cards_list)
    rarity, chara_name = get_chara_name(card_id)
    rarity_desc = '【稀有】的' if rarity == 1 else ''
    db.add_card_num(ev.group_id, ev.user_id, card1_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card2_id, -1)
    db.add_card_num(ev.group_id, ev.user_id, card_id)
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
    card1_id = get_card_id(card1_name)
    card2_id = get_card_id(card2_name)
    if not card1_id or card1_id not in cards:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card1_name)}, 若为稀有卡请在前面加上"稀有"二字')
    if not card2_id or card2_id not in cards:
        await bot.finish(ev, f'错误: 无法识别{get_card_name_with_rarity(card2_name)}, 若为稀有卡请在前面加上"稀有"二字')
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


@sv.on_prefix('查看仓库')
async def storage(bot, ev: CQEvent):
    if len(ev.message) == 1 and ev.message[0].type == 'text' and not ev.message[0].data['text']:
        uid = ev.user_id
    elif ev.message[0].type == 'at':
        uid = int(ev.message[0].data['qq'])
    else:
        await bot.finish(ev, '参数格式错误, 请重试')
    row_num = math.ceil(len(cards)/COL_NUM)
    base = Image.open(DIR_PATH + '/frame.png')
    base = base.resize((40+COL_NUM*80+(COL_NUM-1)*10, 40+row_num*80+(row_num-1)*10), Image.ANTIALIAS)
    cards_num = db.get_cards_num(ev.group_id, uid)
    for index, id in enumerate(cards):
        row_index = index // COL_NUM
        col_index = index % COL_NUM
        card_id = cards[index]
        pic_path = DIR_PATH + '/' + card_file_names_all[index]
        f = get_pic(pic_path, cards_num[card_id]) if card_id in cards_num else get_grey_pic(pic_path)
        base.paste(f, (30 + col_index * 80 + (col_index - 1) * 10, 30 + row_index * 80 + (row_index - 1) * 10))
    ranking = db.get_group_ranking(ev.group_id, uid)
    ranking_desc = f'#{ranking}' if ranking != -1 else '未上榜'
    total_card_num = sum(cards_num.values())
    rare_card_num = len([card_id for card_id in cards_num if get_card_rarity(card_id) ])
    normal_card_num = len(cards_num) - rare_card_num
    await bot.send(ev, f'{MessageSegment.at(uid)}的仓库:{MessageSegment.image(util.pic2b64(base))}\n持有卡片数: {total_card_num}\n普通卡收集: {normalize_digit_format(normal_card_num)}/{normalize_digit_format(len(card_file_names_normal))}\n稀有卡收集: {normalize_digit_format(rare_card_num)}/{normalize_digit_format(len(card_file_names_rare))}\n图鉴完成度: {normalize_digit_format(len(cards_num))}/{normalize_digit_format(len(cards))}\n当前群排名: {ranking_desc}')