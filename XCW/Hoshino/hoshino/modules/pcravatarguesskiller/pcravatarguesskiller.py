from hoshino import Service, log, priv
from hoshino.typing import CQEvent
from hoshino.modules.priconne import _pcr_data
from hoshino.modules.priconne import chara
from . import main

import hoshino
import os

sv_help = '''
杀手~
'''.strip()

sv = Service(
    name = '猜头像杀手',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = False, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助猜头像杀手"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

logger = log.new_logger('avatarguess_killer', hoshino.config.DEBUG)


ANSWERS_DIC_CACHE = {}

@sv.on_keyword('生成json')
async def create_json(bot, ev: CQEvent):
    if not priv.check_priv(ev ,priv.ADMIN):
        await bot.send(ev , '该操作需要管理员权限', at_sender=True)
        return
    update = 'N'
    status = main.get_sprite_chara_icon_name_str_list(update)
    if status[0]:
        await bot.send(ev, status[1])
    else:
        await bot.send(ev, status[1])
        
@sv.on_keyword('更新json')
async def update_json(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev , '该操作需要管理员权限', at_sender=True)
        return
    update = 'Y'
    status = main.get_sprite_chara_icon_name_str_list(update)
    if status[0]:
        await bot.send(ev, status[1])
    else:
        await bot.send(ev, status[1])
        
@sv.on_keyword('生成sprite图')
async def test2(bot, ev: CQEvent):
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '该操作需要管理员权限', at_sender=True)
        return
    update = 'N'
    status = main.draw_sprite_image(update)
    if status[0]:
        await bot.send(ev, status[1])
    else:
        await bot.send(ev, status[1])

@sv.on_keyword('更新sprite图')
async def test2(bot, ev: CQEvent):
    if not priv.check_priv(ev,priv.ADMIN):
        await bot.send(ev, '该操作需要管理员权限', at_sender=True)
        return
    update = 'Y'
    status = main.draw_sprite_image(update)
    if status[0]:
        await bot.send(ev, status[1])
    else:
        await bot.send(ev, status[1])
        

@sv.on_prefix(('猜猜这个图片是哪位角色头像的一部分'))
async def bot_crazy(bot, ev: CQEvent):
    template_image_name = ''
    for seg in ev.message:
        if (seg.type == 'image'):
            template_image_name = main.download_template_image(seg.data['url'])
            if (template_image_name == ""):
                logger.error(f'Fail to find a image in message [{ev.message}]')
                return
            else:
                break
    result = main.transform_coordinate_to_chara_id(template_image_name) 
    if result[0]:
        chara_name = chara.fromid(result[1]).name
        #it could be very hard to answer faster than bot. please add a time.sleep. onegai
        await bot.send(ev, chara_name)
    if not result[0] and result[1] != '':
        await bot.send(ev, result[1])
        
    
            