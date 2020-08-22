from datetime import *
import string
import random
from . import util

import nonebot
from quart import request, Blueprint, jsonify, render_template

from hoshino import Service, priv

sv = Service('homework_', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)
auth = Blueprint('auth', __name__, url_prefix='/auth', template_folder="./vue", static_folder='./vue',
                 static_url_path='')
bot = nonebot.get_bot()
app = bot.server_app

manage_password = '12345678'  # 管理密码请修改


@auth.route('/')
async def index():
    return await render_template("index.html")


@auth.route('/api/login', methods=['POST'])
async def login_auth():
    password = request.args.get('password')
    if password == manage_password:
        return 'success'
    return 'failed'


@auth.route('/api/get/key', methods=['GET'])
async def get_key():
    password = request.args.get('password')
    if password != manage_password:
        return 'failed'
    return jsonify(util.get_key_list())


@auth.route('/api/add/key', methods=['POST'])
async def add_key():
    if request.method == 'POST':
        duration = int(request.args.get('duration'))
        num = int(request.args.get('num'))
        for _ in range(num):
            util.add_key(duration)
        return 'success'
    return 'failed'


@auth.route('/api/del/key', methods=['DELETE'])
async def del_key():
    if request.method == 'DELETE':
        key = request.args.get('key')
        return jsonify(util.del_key(key))


@auth.route('/api/update/key', methods=['POST'])
async def update_key():
    key = request.args.get('key')
    duration = int(request.args.get('duration'))
    return jsonify(util.update_key(key, duration))


@auth.route('/api/get/group', methods=['GET'])
async def get_group():
    password = request.args.get('password')
    if password != manage_password:
        return 'failed'
    return jsonify(util.get_authed_group_list())


@auth.route('/api/activate', methods=['POST'])
async def activate_group():
    key = request.args.get('key')
    gid = request.args.get('gid')
    if util.reg_group(gid, key):
        return 'success'
    return 'failed'
