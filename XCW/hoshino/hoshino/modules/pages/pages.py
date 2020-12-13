import os
import nonebot
from quart import request,session,redirect,Blueprint,url_for,render_template,jsonify,session
from nonebot.exceptions import CQHttpError
from hoshino import R, Service, priv, config
from pathlib import Path

public_address = config.IP#修改为服务器公网ip


sv = Service('网页端', visible= True, enable_on_default= True, bundle='网页端', help_='''
- [#帮助] 帮助页面的网页端
- [手册] 打开会战手册
- [主页] 浏览主页
'''.strip())

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
    return await render_template('main.html')

@hp.route('/xcwhelp')
async def index():
    return await render_template('help.html')
    
@tk.route('/xcwthanks')
async def index():
    return await render_template('thanks.html')

@ab.route('/xcwabout')
async def index():
    return await render_template('about.html')

@sc.route('/xcwmanual')
async def index():
    return await render_template('manual.html')

@js.route('/xcw404')
async def index():
    return await render_template('404.html')

@sv.on_fullmatch("主页",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwmain')

@sv.on_fullmatch("#帮助",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwhelp')
    
@sv.on_fullmatch("手册",only_to_me=False)
async def get_uploader_url(bot, ev):
    cfg = config.__bot__
    await bot.send(ev,f'http://{public_address}:{cfg.PORT}/xcwmanual')
