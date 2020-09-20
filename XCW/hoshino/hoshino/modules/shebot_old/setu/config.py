import re

DEFAULT_ONLINE = False #是否默认在线涩图
WITH_URL = False #发图是是否附带链接
R18_PATH = '../miraiGO/data/images/r18_setu' #r18 涩图保存路径,必须在酷Q图片路径下
NR_PATH = '../miraiGO/data/images/nr18_setu'#非r18涩图保存路径，必须在酷Q图片路径下
SEARCH_PATH = '../miraiGO/data/images/search_setu'#搜索结果保存路径，必须在酷Q图片路径下
COMMON_RE = re.compile('^来?([1-5])?[份点张]?[涩色瑟]图(.{0,10})$')#非r18匹配正则表达式
SECRET_RE = re.compile('^就这不够色([1-5])?$')#r18正则表达式



