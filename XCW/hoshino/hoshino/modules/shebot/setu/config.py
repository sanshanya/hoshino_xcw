import re

APIKEY = 'XXXXXXXXXXXXXXXXXXXXX'                                        #填lolicon apikey
ONLINE_MODE = True                                                      #选择在线模式还是本地模式,选择False时，程序将不会访问api和启动下载线程，插件发送本地涩图
WITH_URL = False                                                         #是否发图时附带链接
DAILY_MAX_NUM = 10                                                       #每日最大涩图数(仅在在线模式下生效)
EXCEED_NOTICE = f'您今天已经冲过{DAILY_MAX_NUM}次了，请明早5点后再来！' 
TOO_FREQUENT_NOTICE = f'您冲得太快了，请稍后再来~'

######################################
#本地模式涩图文件夹请在酷q image目录下找nr18_setu,r18_setu文件夹，分别代表非r18和r18色图


