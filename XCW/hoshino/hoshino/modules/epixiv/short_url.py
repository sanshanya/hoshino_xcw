import json
import requests
from urllib import parse

from . import util

setting = util.get_config().setting


def short(url: str):
    if not setting.short_url_enable:
        return url

    data = {
        'key': setting.short_key,
        'url': parse.quote(url)
    }
    try:
        res = json.loads(requests.get(setting.short_api.format(**data), timeout=30).text, object_hook=util.Dict)
    except TimeoutError:
        print('short url time out')
        return url

    if setting.short_error and res[setting.short_error] == setting.short_error_value:
        print('short url error: %s' % res.msg)
        return url

    return res[setting.short_json_str]
