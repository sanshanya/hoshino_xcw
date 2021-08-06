import datetime
import json
import math
from pathlib import Path

from PIL import Image, PngImagePlugin

from ..util import Dict, cache, get_path, get_font, pil2b64
from ..imghandler import draw_text_by_line, image_array, easy_paste
from hoshino import aiorequests
from bs4 import BeautifulSoup

BASE_URL = 'https://spiral-abyss.appsample.com'

oLookup = {}
s = 'no3yz5{q9kvxs6:,_-ODGW4AtiPj7mZerQXMBpabU1Jlfg}CNHY0VFRc"SEdI28KTwuLh'
b64char = 'dAHBGOQNv"Cg,WPrU:fX93kJK-{bDVjLESs}oqMRmy0Til4nt_8c1pIZFYa6euwx5z72h'

# with open(os.path.join(os.path.dirname(__file__), 'character.json'), 'r', encoding="utf-8") as f:
#     character_json: dict = json.loads(f.read())

assets_dir = Path(get_path('assets'))


async def decode(raw_data):
    if not oLookup:
        for i, v in enumerate(b64char):
            oLookup[v] = s[i]
    ret = ''
    for i, v in enumerate(raw_data):
        ret += oLookup.get(raw_data[i], raw_data[i])
    return json.loads(ret, object_hook=Dict)


@cache(ttl=datetime.timedelta(hours=12))
async def __get_build_id__():
    res = await aiorequests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(await res.content, 'lxml')
    data = soup.find('script', {"id": "__NEXT_DATA__"}).next
    data = json.loads(data, object_hook=Dict)
    # floorDataRaw = await decode(data.props.pageProps.floorDataRaw)
    # floorRaw = await decode(data.props.pageProps.floorRaw)
    return data.buildId


async def get_abyss_data(floor):
    json_url = '%s/_next/data/%s/zh/floor-%s.json' % (BASE_URL, await __get_build_id__(), floor or '12')
    res = await aiorequests.get(json_url, timeout=10)
    json_data = await res.json(object_hook=Dict)
    return await decode(json_data.pageProps.floorDataRaw)


@cache(ttl=datetime.timedelta(hours=2), arg_key='floor')
async def abyss_use_probability(floor):
    if not floor.isdigit() or int(floor) < 9 or int(floor) > 12:
        return '仅支持9-12层数据'

    data = await get_abyss_data(floor=floor)

    pr_list = {}
    for char_id in data.deploy_count:
        pr = data.deploy_count[char_id] / data.roles_count[char_id]
        pr_list[char_id] = pr * 100

    avatar_cards = []
    for name, pr in sorted(pr_list.items(), key=lambda x: x[1], reverse=True):
        card = Image.open(assets_dir / "chara_card" / f'{name}.png')
        draw_text_by_line(card, (0, 235), f'%s%%' % ('%.2f' % pr), get_font(35), '#475463', 226, True)
        avatar_cards.append(card)

    chara_bg = Image.new('RGB', (1080, math.ceil(len(avatar_cards) / 4) * 315), '#f0ece3')
    chara_img = image_array(chara_bg, avatar_cards, 4, 35, 0)

    info_card = Image.new('RGB', (chara_img.size[0], chara_img.size[1] + 120), '#f0ece3')
    floor = '深境螺旋[第%s层]角色使用率\n' % data.floor
    draw_text_by_line(info_card, (0, 35), floor, get_font(50), '#475463', 1000, True)
    easy_paste(info_card, chara_img.convert('RGBA'), (0, 120))

    info_card.thumbnail((info_card.size[0] * 0.7, info_card.size[1] * 0.7))
    return pil2b64(info_card)


@cache(ttl=datetime.timedelta(hours=2), arg_key='floor')
async def abyss_use_teams(floor):
    if not floor.isdigit() or int(floor) < 9 or int(floor) > 12:
        return '仅支持9-12层数据'
    data = await get_abyss_data(floor=floor)
    best_data_len = 3

    def get_cards(ids):
        avatar_cards = []
        for char_ids in ids:
            for c_id in char_ids.split('_'):
                card: PngImagePlugin.PngImageFile = Image.open(assets_dir / "chara_card" / f'{c_id}.png')
                card = card.crop((0, 0, card.size[0], card.size[1] - 55))
                avatar_cards.append(card)
        temp_size = avatar_cards[0].size
        bg = Image.new('RGB', (temp_size[0] * 4, temp_size[1] * best_data_len), '#f0ece3')
        return image_array(bg, avatar_cards, 4, 10, 0).convert('RGBA')

    space = 100
    chara_bg = None
    for i in [1, 2, 3]:
        avatar_a = get_cards(list(data['best_%s_a' % i])[0:best_data_len])
        avatar_b = get_cards(list(data['best_%s_b' % i])[0:best_data_len])

        row_item = Image.new('RGB', (avatar_a.size[0] * 2 + space, avatar_a.size[1]), '#f0ece3')
        easy_paste(row_item, avatar_a, (0, 0))
        easy_paste(row_item, avatar_b, (avatar_a.size[0] + space, 0))
        team_space = 100
        if not chara_bg:
            chara_bg = Image.new('RGB', (
                avatar_a.size[0] * 2 + space,
                row_item.size[1] * 3 + team_space * 3),
                                 '#f0ece3')

        team_item_y = (i - 1) * (row_item.size[1] + team_space) + team_space
        title_y = team_item_y - (team_space * 0.8)
        draw_text_by_line(chara_bg, (0, title_y), f'第{i}间', get_font(50), '#475463', 1000, True)
        easy_paste(chara_bg, row_item.convert('RGBA'), (0, team_item_y))

    info_card = Image.new('RGB', (chara_bg.size[0], chara_bg.size[1] + 120), '#f0ece3')
    floor = '深境螺旋[第%s层] 上间/下间 阵容推荐' % data.floor
    draw_text_by_line(info_card, (0, 35), floor, get_font(50), '#475463', 1000, True)
    easy_paste(info_card, chara_bg.convert('RGBA'), (0, 120))

    info_card.thumbnail((info_card.size[0] * 0.7, info_card.size[1] * 0.7))
    return pil2b64(info_card)
