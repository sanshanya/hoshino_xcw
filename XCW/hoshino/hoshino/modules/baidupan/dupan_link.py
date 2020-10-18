import json
import re
import base64
from functools import reduce
from urllib import parse

base64_decodestring = lambda x: base64.decodebytes(x.encode()).decode()
base64_encodestring = lambda x: base64.encodebytes(x.encode()).decode()


def parse_bdpan(link: str):
    f = re.sub(r'\s', '\n', link).split('\n')
    f = map(lambda x: re.sub(r'^bdpan://', '', x, re.I), f)
    f = map(lambda x: x.strip(), f)
    f = filter(lambda x: len(x) > 0, f)
    f = map(lambda x: str(base64_decodestring(x)), f)
    f = map(lambda x: re.search(r'([\s\S]+)\|([\d]{1,20})\|([\dA-z]{32})\|([\dA-z]{32})', x).groups(), f)
    f = map(lambda x: dulink.make(name=x[0], size=x[1], md5=x[2].lower(), md5s=x[3].lower()), f)
    return list(f)


def parse_ali213(link: str):
    f = re.sub(r'\s', '', link)[len('BDLINK'):]
    f = bytearray(base64.b64decode(f))
    if f[0:5] != b'BDFS\x00':
        return None

    def read_number(index, size):
        return reduce(lambda s, x: (s << 8) + x, reversed(f[index: index + size]), 0)

    def read_uint(index):
        return read_number(index, 4)

    def read_ulong(index):
        return read_number(index, 8)

    def read_hex(index, size):
        return ''.join(map(lambda x: '%02x' % x, f[index: index + size]))

    def read_unicode(index, size):
        if size & 1:
            size += 1
        return json.loads('"%s"' % re.sub(r'(\w{2})(\w{2})', r'\\u\2\1', read_hex(index, size)))

    total = read_uint(5)
    ptr = 9
    ff = list()
    for _ in range(total):
        # size (8 bytes)
        # MD5 + MD5S (0x20)
        # nameSize (4 bytes)
        # Name (unicode)
        d = dulink()
        d.size = read_ulong(ptr + 0)
        d.md5 = read_hex(ptr + 8, 0x10)
        d.md5s = read_hex(ptr + 0x18, 0x10)
        name_size = read_uint(ptr + 0x28) << 1
        ptr += 0x2C
        d.name = read_unicode(ptr, name_size)
        ptr += name_size
        ff.append(d)
    return ff


def parse_pcsgo(link: str):
    f = link.split('\n')
    f = map(lambda x: x.strip(), f)
    f = filter(lambda x: len(x) > 0, f)
    f = map(lambda x: re.search(
        r'-length=([\d]{1,20}) -md5=([\dA-z]{32}) -slicemd5=([\dA-z]{32}) (?:-crc32=\d{1,20} )?"/?(.+)"', x).groups(),
            f)
    f = map(lambda x: dulink.make(name=x[3], size=x[0], md5=x[1].lower(), md5s=x[2].lower()), f)
    return list(f)


def parse_mengji(link: str):
    f = link.split('\n')
    f = map(lambda x: x.strip(), f)
    f = filter(lambda x: len(x) > 0, f)
    f = map(lambda x: re.search(r'([\dA-z]{32})#([\dA-z]{32})#([\d]{1,20})#([\s\S]+)', x).groups(), f)
    f = map(lambda x: dulink.make(name=x[3], size=x[2], md5=x[0].lower(), md5s=x[1].lower()), f)
    return list(f)


def parse_bdlink(link: str):
    f = link.split('\n')
    f = map(lambda x: x.strip(), f)
    f = filter(lambda x: len(x) > 0, f)
    f = map(lambda x: re.search(r'bdlink=([^&#?]*)', x, re.I).group(1), f)
    f = map(lambda x: base64_decodestring(x), f)
    f = map(lambda x: pan_parse(x), f)
    ff = list()
    for x in f:
        ff.extend(x)
    return ff


def to_bdlink(ru_list):
    ru_list = ru_list if isinstance(ru_list, list) else [ru_list]
    f = map(lambda x: x if isinstance(x, dulink) else dulink.make(**x), ru_list)
    f = map(lambda x: x.to_mengji_link(), f)
    ff = []
    for x in f:
        ff.append(x)
    return 'https://pan.baidu.com/#bdlink=%s' % (base64_encodestring('\n'.join(ff)).replace('\n', ''))


def pan_parse(pan_url: str):
    pan_url = pan_url.strip()
    mc = re.search(r'mc=(\S+)', pan_url)
    if mc:
        pan_url = parse.unquote(mc.group(1))
    if re.search(r'^bdpan:', pan_url, re.I):
        return parse_bdpan(pan_url)
    elif re.search(r'^BDLINK', pan_url):
        return parse_ali213(pan_url)
    elif re.search(r'^(BaiduPCS-Go|rapidupload)', pan_url, re.I):
        return parse_pcsgo(pan_url)
    elif re.search(r'.*?bdlink=', pan_url, re.I):
        return parse_bdlink(pan_url)
    else:
        try:
            return parse_mengji(pan_url)
        except AttributeError:
            return False


class dulink:
    def __init__(self):
        self.name = None
        self.size = None
        self.md5 = None
        self.md5s = None

    @classmethod
    def make(cls, name, size, md5, md5s):
        c = cls()
        c.name = name
        c.size = size
        c.md5 = md5
        c.md5s = md5s
        return c

    def to_pandownload_link(self):
        return 'bdpan://%s' % base64_encodestring('%s|%s|%s|%s' % (self.name, self.size, self.md5, self.md5s)).replace(
            '\n', '')

    def to_mengji_link(self):
        return '%s#%s#%s#%s' % (self.md5.upper(), self.md5s.upper(), self.size, self.name)

    def to_pcsgo_link(self):
        return 'BaiduPCS-Go rapidupload -length=%s -md5=%s -slicemd5=%s "%s"' % (
            self.size, self.md5.lower(), self.md5s.lower(), self.name.replace('"', '%22'))

    def __repr__(self):
        return 'size: %d, md5: %s, md5s: %s, name: %s' % (self.size, self.md5, self.md5s, self.name)
