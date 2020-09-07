# require pycryptodomex
import base64
import binascii
import json
import os
from http.cookiejar import Cookie

import httpx
from Cryptodome.Cipher import AES

BASE_URL = "http://music.163.com"
MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
PUBKEY = "010001"
NONCE = b"0CoJUm6Qyw8W8jud"


def encrypted_request(text):
    # type: (str) -> dict
    data = json.dumps(text).encode("utf-8")
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16),
             int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


# 搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*
def search(keywords, stype=1, offset=0, total="true", limit=50):
    song_list = []
    path = "/weapi/search/get"
    params = dict(s=keywords, type=stype, offset=offset,
                  total=total, limit=limit)
    data = request('POST', path, params)
    if data:
        for item in data['result']['songs'][:3]:
            song_list.append(
                {
                    'name': item['name'],
                    'id': item['id'],
                    'artists': ' '.join(
                        [artist['name'] for artist in item['artists']]
                    ),
                    'type': '163'
                }
            )
        return song_list
    return data


def request(method, path, params={},  custom_cookies={}):
    endpoint = "{}{}".format(BASE_URL, path)
    data = None

    cookie = {}
    for key, value in custom_cookies.items():
        cookie = make_cookie(key, value)

    params = encrypted_request(params)
    try:
        resp = httpx.request(method, endpoint, data=params,
                             cookies=cookie, timeout=3)
        data = resp.json()
    finally:
        return data


# 生成Cookie对象
def make_cookie(name, value):
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain="music.163.com",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
    )


if __name__ == "__main__":
    song_list = search('起风了')
    if song_list:
        for song in song_list:
            print(song)
