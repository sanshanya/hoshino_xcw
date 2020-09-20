import os
import nonebot
from quart import request,session,redirect,Blueprint,url_for,render_template,jsonify,session
from nonebot.exceptions import CQHttpError
from hoshino import R, Service, priv, config
from pathlib import Path
import hoshino
from hoshino.util import DailyNumberLimiter
from hoshino import R, Service

public_address = hoshino.config.IP#修改为服务器公网ip
HwManagePwd = 'xcw'#删除文件密码
loginUserName = 'xcw'#登录账户
loginPassword = 'xcw'#登录密码
bot_name = hoshino.config.NICKNAME#机器人名字
group_name = '镜华的相册'#公会名

sv = Service('pages', manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)
work_env = Path(os.path.dirname(__file__))
homework_folder = work_env.joinpath('img')
static_folder = work_env.joinpath('static')
ma = Blueprint('ma',__name__,template_folder='templates',static_folder=static_folder)
hp = Blueprint('hp',__name__,template_folder='templates',static_folder=static_folder)
tk = Blueprint('tk',__name__,template_folder='templates',static_folder=static_folder)
ab = Blueprint('ab',__name__,template_folder='templates',static_folder=static_folder)
sc = Blueprint('sc',__name__,template_folder='templates',static_folder=static_folder)
js = Blueprint('js',__name__,template_folder='templates',static_folder=static_folder)
bot = nonebot.get_bot()
app = bot.server_app
sv.logger.info(homework_folder)



@ma.route('/xcwmain')
async def index():
    return await render_template('main.html',bot_name=bot_name, group_name=group_name)

@hp.route('/xcwhelp')
async def index():
    return await render_template('help.html',bot_name=bot_name, group_name=group_name)
    
@tk.route('/xcwthanks')
async def index():
    return await render_template('thanks.html',bot_name=bot_name, group_name=group_name)

@ab.route('/xcwabout')
async def index():
    return await render_template('about.html',bot_name=bot_name, group_name=group_name)

@sc.route('/xcwmanual')
async def index():
    return await render_template('manual.html',bot_name=bot_name, group_name=group_name)

@js.route('/xcw404')
async def index():
    return await render_template('404.html',bot_name=bot_name, group_name=group_name)

@sv.on_fullmatch("主页",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwmain')

@sv.on_fullmatch("帮助",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwhelp')
    
@sv.on_fullmatch("手册",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwmanual')
