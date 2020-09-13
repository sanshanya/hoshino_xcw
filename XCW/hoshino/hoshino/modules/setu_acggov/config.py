import hoshino
APIKEY = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJrZWtlbHVvIiwidXVpZCI6IjBjMDgzM2Q2OTViZDRkNTNiNDRjNTk2YTAxNWZmNWRkIiwiaWF0IjoxNTk5MzE2NDI4LCJhY2NvdW50Ijoie1wiZW1haWxcIjpcIjEwNTcwNjk2NzdAcXEuY29tXCIsXCJnZW5kZXJcIjotMSxcImhhc1Byb25cIjowLFwiaWRcIjozNSxcInBhc3NXb3JkXCI6XCJjOTMwMzBiMmUxMDgzZGMxMDFlZGU3ZjgxYjc0MzgwN1wiLFwic3RhdHVzXCI6MCxcInVzZXJOYW1lXCI6XCJrZWtlbHVvXCJ9IiwianRpIjoiMzUifQ.jLpy1w-Qripn043eFcrF59Z4DxMcUjBOSxahulbnlWc' 
IMAGE_PATH = hoshino.config.IMAGE_PATH #宿主图片目录
PER_PAGE = 50   #排行榜每页数量
MODE = 'daily'  #可用模式见 https://api.hcyacg.com/#/public/ranking
PROXY = ''    #代理 仅限http代理 不使用请留空
USE_THUMB = True  #使用略缩图模式
SHOW_TIME = 30     #涩图撤回时间
DAILY_MAX_NUM = 10
FREQ_LIMIT = 60