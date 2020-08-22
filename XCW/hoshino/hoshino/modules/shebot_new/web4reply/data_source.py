import jinja2
import os
import random

from quart.helpers import url_for

static_folder = os.path.join(os.path.dirname(__file__),'static')
template_folder = os.path.join(os.path.dirname(__file__),'templates')
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_folder),
    enable_async=True
    )

async def render_template(template,**kwargs):
    t = env.get_template(template)
    return await t.render_async(**kwargs)

def get_random_str(num:int):
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt
