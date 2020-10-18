import requests
import hashlib
import time
import json

from . import util, api

config = util.get_config()


def __web_sign2__(j, r):
    a = list(range(256))
    p = list(range(256))
    o = []
    v = len(j)
    for q in range(0, 256):
        qv = q % v
        a[q] = ord(j[qv:qv + 1][0])
        p[q] = int(q)
    u = 0
    for q in range(0, 256):
        u = (u + p[q] + a[q]) % 256
        t = p[q]
        p[q] = p[u]
        p[u] = t
    i = u = 0
    for q in range(0, len(r)):
        i = (i + 1) % 256
        u = (u + p[i]) % 256
        t = p[i]
        p[i] = p[u]
        p[u] = t
        k = p[((p[i] + p[u]) % 256)]
        o.append(chr(ord(r[q]) ^ k))
    return o


def __web_sign2base64__(t):
    s = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    a = len(t)
    r = 0
    e = ""
    while a > r:
        o = 255 & ord(t[r])
        r += 1
        if r == a:
            e += s[o >> 2]
            e += s[(3 & o) << 4]
            e += "=="
            break
        n = ord(t[r])
        r += 1
        if r == a:
            e += s[o >> 2]
            e += s[(3 & o) << 4 | (240 & n) >> 4]
            e += s[(15 & n) << 2]
            e += "="
            break
        i = ord(t[r])
        r += 1
        e += s[o >> 2]
        e += s[(3 & o) << 4 | (240 & n) >> 4]
        e += s[(15 & n) << 2 | (192 & i) >> 6]
        e += s[63 & i]
    return e


sign = ''
timestamp = 0


def gen_web_sign():
    url = 'https://pan.baidu.com/api/gettemplatevariable?app_id=250528&channel=chunlei&clienttype=0&fields=[%22sign1%22,%22sign2%22,%22sign3%22,%22timestamp%22]&web=1'
    text = requests.get(url, headers=api.get_randsk_headers(), timeout=30).text
    try:
        info = json.loads(text)
    except json.JSONDecodeError:
        info = json.loads(text[3:])

    if not info['errno'] == 0:
        return False, 0
    global sign, timestamp

    result = util.dict_to_object(info['result'])
    sign = __web_sign2__(result.sign3, result.sign1)
    sign = __web_sign2base64__(''.join([str(i) for i in sign]))
    timestamp = result.timestamp
    return sign, timestamp


def get_web_sign():
    if timestamp + config.rules.sign_cache_time * 60 * 60 < time.time() or timestamp == 0:
        print('刷新sign')
        return gen_web_sign()
    return sign, timestamp


def get_sign():
    uid = config.UID
    bduss: str = config.BDUSS
    s_time = int(time.time())
    dev_uid = 'O|' + hashlib.new('md5', bduss.encode()).hexdigest().upper()
    bduss_sha1 = hashlib.sha1(str.encode(bduss)).hexdigest() + f'{uid}'
    key = b'\x65\x62\x72\x63\x55\x59\x69\x75\x78\x61\x5a\x76\x32\x58\x47\x75\x37\x4b\x49\x59\x4b\x78\x55\x72\x71\x66\x6e\x4f\x66\x70\x44\x46'
    bduss_sha1 = bduss_sha1.encode() + key
    rand_sha1 = bduss_sha1 + str(s_time).encode() + dev_uid.encode()
    rand = hashlib.sha1(rand_sha1).hexdigest()
    return s_time, dev_uid, rand
