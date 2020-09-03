from nonebot import on_command, on_notice, on_request,CQHttpError
from hoshino import msghandler, priv, Service

import hoshino, nonebot
import random, re, string
from .web_server import auth
from . import util

import time, pytz
from math import ceil

import re
import asyncio

key_dict = msghandler.key_dict
group_dict = msghandler.group_dict
trial_list = msghandler.trial_list

try:
    config = hoshino.config.authMS.auth_config
except:
    # 保不准哪个憨憨又不读README呢
    hoshino.logger.error('authMS无配置文件!请仔细阅读README')

if config.ENABLE_WEB:
    # 开启web请修改authMS.py
    app = nonebot.get_bot().server_app
    app.register_blueprint(auth)  


@on_command('充值帮助',aliases=('我要充钱','续费帮助','我要续费','👴要充钱'),only_to_me=False)
async def reg_help_chat(session):
    if session.event.detail_type == 'private':
        msg = config.REG_HELP_PRIVATE
    elif session.event.detail_type == 'group':
        msg = config.REG_HELP_GROUP
    else:
        return
    await session.finish(msg)

@on_command('管理员帮助', only_to_me=False)
async def master_help_chat(session):
    if session.event.detail_type == 'group':
        return
    if session.event.user_id not in hoshino.config.SUPERUSERS:
        await session.finish('只有主人才能查看此页帮助')

    await session.finish(config.ADMIN_HELP)