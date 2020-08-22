import nonebot
from .homework import hw
app = nonebot.get_bot().server_app
app.register_blueprint(hw)