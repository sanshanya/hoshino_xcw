from aiocqhttp.event import Event
import nonebot
from .view4reply import reply
from .data_source import get_random_str

app = nonebot.get_bot().server_app
if not app.config.get('SECRET_KEY'):
    app.config['SECRET_KEY'] = 'DFFSGHSHDBBCLSDO'

app.register_blueprint(reply)

from .view4reply import public_address
bot = nonebot.get_bot()
@bot.on_message
async def send_url(ev: Event):
    msg = ev.raw_message
    if msg == '添加自定义回复':
        await bot.send(ev, f'{public_address}:{bot.config.PORT}/reply/show')

