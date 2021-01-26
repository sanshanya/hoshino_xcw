import importlib
import math
import os
import re

import aiohttp

from hoshino import Service, util, priv
from hoshino.modules.pcrsealkiller import Config
from hoshino.typing import CQEvent, MessageSegment

sv_help = '''
自动击杀晒卡海豹，请给机器人管理员或者群主：
- [启用海豹杀手 海豹判定阈值]：如果不输入参数，默认阈值是100
- [禁用海豹杀手] 关闭海豹杀手服务
'''.strip()

sv = Service(
    name = '海豹杀手',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = False, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助海豹杀手"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    


GACHA_KEYWORDS = ['所持角色交换Pt', '持有的角色交換Pt', '所持キャラ交換Pt', '持有的角色交换Pt', '所持キャラ交换Pt', '所持CSPキャラ交換Pt']
FILE_FOLDER_PATH = './hoshino/modules/pcrsealkiller/'
CONFIG_PATH =  f'{FILE_FOLDER_PATH}config.json'
PIC_PATH = f'{FILE_FOLDER_PATH}sealkiller.jpg'
DEFAULT_GACHA_THRESHOLD = 100   # 海豹判定阈值, 如果抽卡次数小于这个阈值，则被判定为海豹
STRICT_MODE = True              # 开启严格模式后，如果未发现"NEW"而抽卡次数小于阈值，仍会撤回消息，但是不禁言（宁可错杀也不可放过海豹）
USE_OPENCV = True               # 是否使用Opencv提高识别精确度


gacha_threshold = Config(CONFIG_PATH)
ocred_images = {}
if USE_OPENCV:
    opencv_util = importlib.import_module('hoshino.modules.pcrsealkiller._opencv_util')


async def is_image_gif_or_meme(bot, img):   # 原有基础上添加表情包过滤功能，感谢HoshinoBot群友们的创意
    r = await bot.call_action(action='get_image', file=img)
    return r['filename'].endswith('gif') or r['size'] < 50000


async def is_possible_gacha_image(bot, ev, img):
    is_gif_or_meme = await is_image_gif_or_meme(bot, img)
    is_ocred = ev.group_id in ocred_images and img in ocred_images[ev.group_id]
    return not (is_gif_or_meme or is_ocred)


def record_ocr(gid, img):
    if gid not in ocred_images:
        ocred_images[gid] = []
    if img not in ocred_images[gid]:
        ocred_images[gid].append(img)


def get_gacha_amount(ocr_result):
    string = re.search('[0-9]+.\+[0-9]+', str(ocr_result))
    if not string:                              # OCR未识别到抽卡次数
        return 0
    gacha_amount = re.match('[0-9]+', string.group(0)).group(0)
    if len(gacha_amount) > 3:                   # OCR识别到多余数字时
        gacha_amount = gacha_amount[math.floor(len(gacha_amount)/2):]
    return int(gacha_amount) if gacha_amount.isdigit() else 0


async def download(url, path):
    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            content = await resp.read()
            with open(path, 'wb') as f:
                f.write(content)


# 返回: 是否需要撤回 是否需要禁言
async def check_image(bot, ev, img):
    try:
        r = await bot.call_action(action='.ocr_image', image=img)
    except:
        return False, False
    kw = is_gacha_screenshot(r)
    if not kw:
        record_ocr(ev.group_id, img)
        return False, False
    else:
        if not is_new_gacha(r, get_text_coordinate_y(r, kw)):
            if not USE_OPENCV:
                if not STRICT_MODE:
                    record_ocr(ev.group_id, img)
                    return False, False
                else:
                    gacha_amount = get_gacha_amount(r)
                    if not gacha_amount or gacha_amount < int(gacha_threshold.threshold[str(ev.group_id)]):
                        return True, False
                    else:
                        record_ocr(ev.group_id, img)
                        return False, False
            else:
                image_path = f'{FILE_FOLDER_PATH}{img}.jpg'
                image_info = await bot.call_action(action='get_image', file=img)
                await download(image_info['url'], image_path)
                new_gacha, error = opencv_util.check_new_gacha(image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                if new_gacha:
                    gacha_amount = get_gacha_amount(r)
                    if not gacha_amount:
                        return True, False
                    elif gacha_amount < int(gacha_threshold.threshold[str(ev.group_id)]):
                        return True, True
                    else:
                        record_ocr(ev.group_id, img)
                        return False, False
                else:
                    if not error:
                        record_ocr(ev.group_id, img)
                        return False, False
                    else:
                        if not STRICT_MODE:
                            record_ocr(ev.group_id, img)
                            return False, False
                        else:
                            gacha_amount = get_gacha_amount(r)
                            if not gacha_amount or gacha_amount < int(gacha_threshold.threshold[str(ev.group_id)]):
                                return True, False
                            else:
                                record_ocr(ev.group_id, img)
                                return False, False
        else:
            gacha_amount = get_gacha_amount(r)
            if not gacha_amount:
                return True, False
            elif gacha_amount < int(gacha_threshold.threshold[str(ev.group_id)]):
                return True, True
            else:
                record_ocr(ev.group_id, img)
                return False, False


def is_gacha_screenshot(ocr_result):
    ocr_result_string = str(ocr_result)
    for keyword in GACHA_KEYWORDS:
        if keyword in ocr_result_string:
            return keyword
    return ''


def get_text_coordinate_y(ocr_result, text):
    text_list = ocr_result['texts']
    for t in text_list:
        if t['text'] == text:
            return t['coordinates'][0]['y']


def is_new_gacha(ocr_result, max_text_coordinate_y):
    text_list = ocr_result['texts']
    for t in text_list:
        if t['text'] == 'NEW' and t['coordinates'][0]['y'] < max_text_coordinate_y:
            return True
    return False


@sv.on_prefix(('启用海豹杀手', '启动海豹杀手'))
async def enable_sealkiller(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    s = ev.message.extract_plain_text()
    if s:
        if s.isdigit() and 0<int(s)<310:
            threshold = int(s)
        else:
            await bot.finish(ev, '参数错误: 请输入1-309之间的整数.')
    else:
        threshold = DEFAULT_GACHA_THRESHOLD
    gacha_threshold.set_threshold(str(ev.group_id), threshold)
    await bot.send(ev, f'海豹杀手已启用, 当前海豹判定阈值为{threshold}抽.')


@sv.on_fullmatch(('禁用海豹杀手', '关闭海豹杀手'))
async def disable_sealkiller(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '抱歉，您非管理员，无此指令使用权限')
    gacha_threshold.delete_threshold(str(ev.group_id))
    await bot.send(ev, f'海豹杀手已禁用')


@sv.on_message()
async def on_input_image(bot, ev: CQEvent):
    if str(ev.group_id) not in gacha_threshold.threshold:
        return
    for seg in ev.message:
        if seg.type == 'image':
            img = seg.data['file']
            need_ocr = await is_possible_gacha_image(bot, ev, img)
            if need_ocr:
                need_delete_msg, need_silence = await check_image(bot, ev, img)
                if need_delete_msg:
                    if need_silence:
                        await bot.send(ev, '检测到海豹行为(╯‵□′)╯︵┻━┻')
                        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
                        await util.silence(ev, 10*60, skip_su=False)
                        await bot.send(ev, 'sealkiller插件提醒您:' + str(MessageSegment.image(f'file:///{os.path.abspath(PIC_PATH)}')) + '拒绝海豹，从我做起')
                    else:
                        await bot.delete_msg(self_id=ev.self_id, message_id=ev.message_id)
                        await bot.send(ev, '虽然没看出你有没有在晒卡，总之消息先撤回了~')