from quart import request, Blueprint, jsonify, render_template

import nonebot

from . import util



activate = Blueprint('activate', __name__, url_prefix='/activate', template_folder="./activate"
                     , static_folder='./activate', static_url_path='')
bot = nonebot.get_bot()
app = bot.server_app


@activate.route("/", methods=["GET", "POST"])
async def activate_group():
    if request.method == "GET":
        if key := request.args.get("key"):
            if gid := request.args.get('group'):
                group_id = int(gid)
                await util.reg_group(group_id, key)
        return await render_template("activate.html")
