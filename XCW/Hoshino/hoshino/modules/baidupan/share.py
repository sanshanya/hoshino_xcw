import requests
import base64
import json
import re
import datetime
import nonebot
from urllib import parse

from . import util, api

config = util.get_config()


# 获取度盘中的surl
def get_surl(pan_url: str):
    surl = re.search(r'surl=([A-Za-z0-9-_]+)', pan_url)
    if surl:
        surl = f'1{surl.group(1)}'
    else:
        surl = re.search(r'(1[A-Za-z0-9-_]+)', pan_url)
        if surl:
            surl = surl.group(1)
        else:
            surl = None
    pwd = re.search(r'#[tq=]*(\S+)', pan_url)
    if pwd:
        pwd = pwd.group(1)
    return surl, pwd


# 验证网盘密码
def verify(surl: str, pwd=None):
    headers = {
        'user-agent': 'netdisk',
        'Referer': 'https://pan.baidu.com/disk/home'
    }

    if pwd:
        url = f'https://pan.baidu.com/share/verify?channel=chunlei&clienttype=0&web=1&app_id=250528&surl={surl}'
        res = json.loads(requests.post(url, data={'pwd': f'{pwd}'.strip()}, headers=headers, timeout=30).text)
        if res['errno'] == 0:
            return res['randsk']
        else:
            return False
    else:
        url = f'https://pan.baidu.com/s/1{surl}'
        res = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        if res.status_code == 302:
            return False
        cookie = res.headers.get('set-cookie')
        BDCLND = re.match(r'BDCLND\=(.+?)\;', cookie)
        if BDCLND:
            return BDCLND.group(1)
        else:
            print('找不到BDCLND')
            return False


# 网盘验证成功后获取分享数据
def get_yun_data(surl: str, randsk: str):
    url = f'https://pan.baidu.com/s/1{surl}'
    res = requests.get(url, headers=api.get_randsk_headers(randsk=randsk), timeout=30).text
    data_str = re.search(r'yunData.setData\(({.+)\);', res)
    if not data_str:
        return False
    return util.dict_to_object(json.loads(data_str.group(1)))


# 获取文件列表
def get_file_list(shareid, uk, randsk, dir_str=None):
    root = 0 if dir_str else 1
    dir_str = f'&dir={parse.quote(dir_str)}' if dir_str else ''
    url = f'https://pan.baidu.com/share/list?app_id=250528&channel=chunlei&clienttype=0&desc=0&num=100&order=name&page=1&root='
    url += f'{root}&shareid={shareid}&showempty=0&uk={uk}{dir_str}&web=1'
    return util.dict_to_object(
        json.loads(requests.get(url, headers=api.get_randsk_headers(randsk=randsk), timeout=30).text))


# 获取真实下载地址
def get_file_dl_link(fs_id, share_id, uk, randsk, sign, timestamp):
    url = f'https://pan.baidu.com/api/sharedownload?app_id=250528&channel=chunlei&clienttype=12&sign='
    url += f'{sign}&timestamp={timestamp}&web=1'
    data = {
        "encrypt": 0,
        "extra": json.dumps({"sekey": parse.unquote(randsk)}),
        "fid_list": f'[{fs_id}]',
        "primaryid": share_id,
        "uk": uk,
        "product": 'share',
        "type": 'nolimit'
    }
    res = requests.post(url, data=data, headers=api.get_randsk_headers(randsk=randsk), timeout=30)
    res = util.dict_to_object(json.loads(res.text))
    if not res.errno == 0:
        return False

    return api.get_real_url_by_dlink(res.list[0]['dlink'])


def handle_file_list(file_list, yun_data, randsk):
    file_info = []
    msg_dir_str = []

    for file in file_list.list:
        file = util.dict_to_object(file)

        if int(file.isdir) == 1:
            if len(file_list.list) == 1:
                file_list = get_file_list(yun_data.shareid, yun_data.uk, randsk, dir_str=file.path)
                if not file_list.errno == 0:
                    return msg_dir_str, file_info
                return handle_file_list(file_list, yun_data, randsk)
            msg_dir_str.append(file.path)
            continue

        dl_link = get_file_dl_link(
            fs_id=file.fs_id,
            share_id=yun_data.shareid,
            uk=yun_data.uk,
            randsk=randsk,
            sign=yun_data.sign,
            timestamp=yun_data.timestamp
        )

        file_info.append({
            'fs_id': file.fs_id,
            'name': f'{file.server_filename}',
            'url': dl_link,
            'size': int(file.size),
            'image': yun_data['photo']
        })
    return msg_dir_str, file_info


# 取消分享
def cancel_share(shareid):
    shareid = shareid if isinstance(shareid, list) else [shareid]
    url = f'https://pan.baidu.com/share/cancel?channel=chunlei&clienttype=0&web=1&channel=chunlei&web=1&app_id=250528&clienttype=0'
    shareid = ",".join([str(i) for i in shareid])
    data = {
        "shareid_list": f'[{shareid}]',
    }
    res = util.dict_to_object(
        json.loads(requests.post(url, data=data, headers=api.get_randsk_headers(), timeout=30).text))

    return res.errno == 0, res.err_msg


# 删除文件
def delete_share(file_path):
    file_path = file_path if isinstance(file_path, list) else [file_path]
    url = f'https://pan.baidu.com/api/filemanager?opera=delete&async=2&onnest=fail&channel=chunlei&web=1&app_id=250528&clienttype=0'
    file_path = ",".join(['"%s"' % i for i in file_path])
    data = {
        "filelist": f'[{file_path}]',
    }
    res = util.dict_to_object(
        json.loads(requests.post(url, data=data, headers=api.get_randsk_headers(), timeout=30).text))

    return res.errno == 0, res.taskid


def auto_cancel_share(shareid, file_path):
    # 8小时后自动删除分享内容
    @nonebot.scheduler.scheduled_job(
        'date',
        run_date=datetime.datetime.now() + datetime.timedelta(hours=config.rules.auto_cancel_share_time)
    )
    def _():
        ok, err_msg = cancel_share(shareid)
        if not ok:
            print(err_msg)
        if config.rules.delete_share_file:
            ok, taskid = delete_share(file_path)
            if not ok:
                print('删除分享文件失败')


# 设置分享文件
def set_share(fs_id, pwd='erin', expire_time=7):
    fs_id = fs_id if isinstance(fs_id, list) else [fs_id]
    url = f'https://pan.baidu.com/share/set?channel=chunlei&clienttype=0&web=1&channel=chunlei&web=1&app_id=250528&clienttype=0'
    fs_id = ",".join([str(i) for i in fs_id])
    data = {
        "schannel": 4,
        "channel_list": '[]',
        "period": expire_time,
        "pwd": pwd,
        "fid_list": f'[{fs_id}]',
    }
    res = util.dict_to_object(
        json.loads(requests.post(url, data=data, headers=api.get_randsk_headers(), timeout=30).text))

    if not res.errno == 0:
        return False, 0

    return res.link, res.shareid


# 创建目录
def create_dir(dir_str):
    url = 'https://pan.baidu.com/api/create?a=commit&channel=chunlei&app_id=250528&channel=chunlei&web=1&app_id=250528&clienttype=0&'
    # url += 'bdstoken=%s&logid=%s' % (yun_data.bdstoken, logid)
    data = {
        'path': dir_str,
        'isdir': 1,
        'size': '',
        'block_list': '[]',
        'method': 'post',
        'dataType': 'json'
    }
    res = requests.post(url, data=data, headers=api.get_randsk_headers(), timeout=30)
    res = util.dict_to_object(json.loads(res.text))
    if res.errno == 0:
        return res.path
    return ''


def get_dir_str(dir_str='default'):
    return f'/{config.rules.dulink_temp_dir}{dir_str}'


# 保存分享文件
def transfer(yun_data, randsk, dir_str=get_dir_str(), init_dir=False):
    logid = base64.b64encode(config.BAIDUID.encode()).decode()
    url = 'https://pan.baidu.com/share/transfer?channel=chunlei&web=1&app_id=250528&clienttype=0&'
    url += 'shareid=%s&from=%s&bdstoken=%s&logid=%s' % (
        yun_data.shareid, yun_data.uk, yun_data.bdstoken, logid)
    fs_ids = map(lambda x: str(x['fs_id']), yun_data.file_list.list)
    f = []
    for i in fs_ids:
        f.append(i)
    fs_ids = ','.join(f)
    data = {
        "fsidlist": f'[{fs_ids}]',
        'path': dir_str
    }
    res = requests.post(url, data=data, headers=api.get_randsk_headers(randsk=randsk), timeout=30)
    res = util.dict_to_object(json.loads(res.text))
    if res.errno == 2 and not init_dir:
        # 创建目录
        has_create = create_dir(dir_str)
        if not has_create:
            print(f'创建目录失败: {dir_str}')
            return False
        return transfer(yun_data, randsk, has_create, True)
        pass
    try:
        return list(map(lambda x: dir_str + x['path'], res.info))
    except Exception as e:
        print(e)
        return False
