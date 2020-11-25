from nonebot import on_command, get_bot

import hoshino

from .constant import config, __version__
from .web_server import auth
from .web_activate import activate



if config.ENABLE_WEB:
    # 开启web请修改authMS.py
    app = get_bot().server_app
    app.register_blueprint(auth)
    app.register_blueprint(activate)


@on_command('充值帮助', aliases=('我要充钱','续费帮助','我要续费','👴要充钱'), only_to_me=False)
async def reg_help_chat(session):
    if session.event.detail_type == 'private':
        msg = config.REG_HELP_PRIVATE
    else:
        msg = config.REG_HELP_GROUP
    #else:
        # 新版QQ已不在有discuss, 所有多人聊天都是群消息
    #    return
    await session.finish(msg)


@on_command('管理员帮助', only_to_me=False)
async def master_help_chat(session):
    if session.event.detail_type == 'group':
        return
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能查看此页帮助')
    await session.finish(config.ADMIN_HELP)


@on_command('授权系统版本', only_to_me=True)
async def check_new_ver_chat(session):
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        return
    await session.finish(f'授权系统当前版本v{__version__}')
