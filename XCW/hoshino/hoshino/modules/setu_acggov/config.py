import hoshino
APIKEY = '' 
IMAGE_PATH = hoshino.config.IMAGE_PATH #宿主图片目录
PER_PAGE = 50   #排行榜每页数量
MODE = 'daily'  #可用模式见 https://api.hcyacg.com/#/public/ranking
PROXY = ''    #代理 仅限http代理 不使用请留空
USE_THUMB = True  #使用略缩图模式

DAILY_MAX_NUM = 10
FREQ_LIMIT = 60
