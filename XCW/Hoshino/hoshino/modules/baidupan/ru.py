import requests
import json
import hashlib
import re
from . import util, api, dupan_link

config = util.get_config()


# 保存秒传文件 文件md5值
def rapidupload(md5, md5s, size, file_name, dir_name='temp/'):
    url = f'https://pan.baidu.com/api/rapidupload?channel=chunlei&clienttype=0&web=1&app_id=250528&rtype=3'
    data = {
        'path': f'{dir_name}{file_name}',
        'content-md5': md5,
        'slice-md5': md5s,
        'content-length': str(size)
    }
    res = json.loads(requests.post(url, data=data, headers=api.get_randsk_headers(), timeout=30).text)
    if not res['errno'] == 0:
        return None
    return res['info']


# 根据下载链接获取秒传信息
def get_rapidupload_info(download_link, ua=None):
    try:
        headers = {
            'User-Agent': ua if ua else api.get_pan_ua(),
            'Cookie': f'BDUSS={config.BDUSS};',
            'Range': 'bytes=0-262143'
        }
        res = requests.get(download_link, headers=headers, timeout=30, allow_redirects=False)
        md5 = res.headers.get('Content-MD5').upper()
        md5s = hashlib.new('md5', res.content).hexdigest().upper()
        size = res.headers.get('x-bs-file-size')
        file_name = re.search(r'filename="(.+)"', res.headers.get('Content-Disposition')).group(1)
        file_name = file_name.encode('raw_unicode_escape').decode('utf-8')
        return dupan_link.dulink.make(file_name, size, md5, md5s)
    except Exception as e:
        print(e)
        return None
