import requests
import json
from urllib import parse

from . import util, sign

config = util.get_config()


def get_pan_ua():
    # return 'netdisk;2.2.51.6;netdisk;10.0.63;PC;android-android'
    return 'netdisk;android-android;'


def get_randsk_headers(ua=None, randsk=None):
    randsk = f'; BDCLND={randsk}' if randsk else ''
    ua = ua if ua else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.514.1919.810 Safari/537.36'
    return {
        'Referer': 'https://pan.baidu.com/disk/home?',
        'User-Agent': ua,
        'Cookie': f'BDUSS={config.BDUSS}; STOKEN={config.STOKEN}{randsk}'
    }


def get_real_url_by_dlink(dlink, urls: list = None, ua=None):
    if not dlink:
        return ''
    headers = {
        'User-Agent': ua if ua else 'LogStatistic',  # 这里好坑啊 不能使用pan的ua
        'Cookie': f'BDUSS={config.BDUSS};'
    }
    try:
        real_link = requests.get(dlink, headers=headers, timeout=30, allow_redirects=False)
        if real_link.status_code == 302:
            return real_link.headers.get('Location')
        if real_link.status_code == 403 and urls:
            urls.pop(0)
            return get_real_url_by_dlink(urls[0], urls, ua=ua)
        if real_link.status_code == 31360:
            return 'bduss 已过期,请重新获取'
        return ''
    except requests.exceptions.SSLError:
        if not urls or not isinstance(urls, list):
            return ''
        urls.pop(0)
        return get_real_url_by_dlink(urls[0], urls, ua=ua)


# 获取度盘内的文件真实下载地址
def get_web_file_url(fs_id: list):
    sign_str, timestamp = sign.get_web_sign()
    url = f'https://pan.baidu.com/api/download?type=dlink&channel=chunlei&web=1&app_id=250528&clienttype=0&' \
          f'sign={parse.quote(sign_str)}&timestamp={timestamp}&fidlist=%5B{",".join([str(i) for i in fs_id])}%5D'
    info = util.dict_to_object(json.loads(requests.get(url, headers=get_randsk_headers(), timeout=30).text))
    if not info.errno == 0:
        return []
    url = []
    for dl in info.dlink:
        url.append(get_real_url_by_dlink(dl['dlink']))
    return url


# 获取本地下载地址
def get_local_download_link(path: str):
    try:
        path = parse.quote(path).replace('/', '%2F')
        s_time, dev_uid, rand = sign.get_sign()
        url = f'https://pcs.baidu.com/rest/2.0/pcs/file?app_id=250528&method=locatedownload&path=' \
              f'{path}&ver=2&time={s_time}&rand={rand}&devuid={dev_uid}'
        headers = {
            'User-Agent': get_pan_ua(),
            'Cookie': f'BDUSS={config.BDUSS};'
        }
        info = util.dict_to_object(
            json.loads(requests.get(url, headers=headers, timeout=30).text))
        if info.get('error_code'):
            return False
        if not info.get('urls'):
            return False

        return list(map(lambda x: 'https://' + x['url'][7:] if x['url'][:7] == 'http://' else x['url'], info.urls))
    except Exception as e:
        print('get_local_download_link error:\n %s' % e)
        return False
