"""
----------------请阅读注释!!!!
--------------请阅读注释!!!!!!
-----------请阅读注释!!!!!!!!!
"""
###################################
'''---hoshino监听的端口与ip-----'''
PORT = 8080           #本条请保持默认
HOST = '0.0.0.0'      # 本条请保持默认,本地部署使用此条配置（QQ客户端和bot端运行在同一台计算机）
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）
###################################
DEBUG = False           # 调试模式,不建议开启
###################################
'''---拥有最高权限的用户们的QQ---'''
SUPERUSERS = [1234567895]    # 填写超级用户的QQ号，可填多个用半角逗号","隔开
PYS ={1764461263}            #高级权限用户的QQ号
###################################
'''---------昵称及网址----------'''
NICKNAME = r'镜华|小仓唯|露娜|at,qq=1764461263'           # 设置bot的昵称，at，qq=xxxxxxxx处为bot的QQ号,呼叫昵称等同@bot,推荐修改
IP = '333.33.33.3'                                      #修改为你的服务器ip,推荐修改
public_address = '333.33.33.3:8080'                     #修改为你的服务器ip+端口,推荐修改
PassWord = '123456'                                           #登录一些只限维护人知道密码的网页
###################################
'''
-----上方内容请务必结合注释修改-----
-----下面的内容请按需求修改---------
'''
###################################

'''
-------------apikeys---------------
lolicon_api,相关插件setu_mix,申请地址https://api.lolicon.app/#/setu?id=apikey
acggov_api,相关插件setu_mix,申请地址https://www.acgmx.com/
shitu_api,相关插件shitu,申请地址http://saucenao.com/
jjc_api,相关插件arena,申请地址https://www.pcrdfans.com/bot
tenxun_api,相关插件aichat,申请地址https://ai.qq.com/,已经为你默认准备了一个,但建议自行申请进行个性定制
'''
lolicon_api = ''                                        
acggov_api = '' 
shitu_api = ''                                     
jjc_api = ""
tenxun_api_ID = '2154581933'   #仅供测试用的默认apikey，画像：名字：冰川镜华 年龄：8岁
tenxun_api_KEY = 'gtv1yCMqKSKSoeuD'  #建议更换
baidu_api_ID = ''    
baidu_api_KEY = ''
baidu_api_SECRET = ''                                 
###################################
'''-----------pixiv账号----------'''
pixiv_id = ''                           #pixiv账号,无需会员
pixiv_password = ''                     #pixiv账号对应的密码
###################################
'''-------本部分建议不要改动-------'''
IMAGE_PATH = "../go-cqhttp/data/images"                 #MiraiGO用这条,保持默认即可
COMMAND_START = {''}    # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()     # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# 发送图片的协议
# 可选 http, file, base64
# 当QQ客户端与bot端不在同一台计算机时，可用http协议
RES_PROTOCOL = 'file'
# 资源库文件夹，需可读可写，windows下注意反斜杠转义
RES_DIR = "../res/"
# 使用http协议时需填写，原则上该url应指向RES_DIR目录
RES_URL = 'http://127.0.0.1:5000/static/'
###################################
'''
插件开关
初次尝试部署时请先保持默认
如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
切忌一次性开启多个
'''
###################################
MODULES_ON = {
    'botmanage',
    'dice',#骰子
    'groupmaster',#群聊基础功能
    'hourcall',#报时功能
    # 'kancolle',#舰娘的远征
    # 'mikan',#蜜柑订阅番剧
    #'pcrclanbattle',#hoshinobot自带尚待完善
    'priconne',#抽卡/竞技场之类的集合
    #'setu',#原生色图功能
    'translate',#原生翻译功能
    # 'twitter',#推特订阅，需要配置本目录下的twitter.py
    'hourcallyao',#买药提醒
    'reload',#重启
    'tarot',#塔罗牌
    'flac',#搜无损音乐  
    'shifan',#识别番剧
    'clanbattle_report',#会战报告生成，需要修改路径
    'voiceguess',#猜语音
    #'eclanrank',
    'aichat',#需要apikey，用前修改概率
    'hiumsentences',#网抑云语录
    'generator',#营销文生成等五个小功能
    'ontree_scheduler',#挂树优化提醒
    'eqa',#问答功能2
    'russian',#俄罗斯轮盘赌
    #'explosion',#每天一发惠惠
    'boxcolle',#BOX查询
    'timeline',#轴上传
    'picapi',#自定义拉取图片
    'aircon',#群空调
    #'bilisearchspider',#b站订阅
    'pcravatarguess',#图片猜角色
    'pcrdescguess',#通过角色描述猜角色,需要设置go-cqhttp的心跳间隔,推荐3
    'nmsl',#抽象抽象抽抽抽像像像
    #'baidupan',#百度盘解析
    'meme_web',#memegenerator的web化,勿同时开启
    'pcrmiddaymusic',#公主连结午间音乐
    'image_generate',#取代原image
    'music',#点歌插件
    'pcrmemorygames',#公主连结记忆小游戏
    #'epixiv',#需要pixiv站账号
    #'emergeface',#换脸插件,需要apikey
    'eclanblack',#兰德索尔黑名单
    'memberguess',#猜群友头像
    'anticoncurrency',# 反并发插件
    'portune',#运势插件
    'pokemanpcr',#戳一戳卡片小游戏
    'pages',#bot网页端
    'clanbattle_rank',#会战排名查询插件
    #'clanbattle_info',#自动报刀插件,开启前请按说明，配置难度较高
    'nbnhhsh',#将抽象短语转化为好好说话
    'nowtime',#发送"报时"有惊喜
    'pcrsealkiller',#海豹杀手
    'setu_mix',#俩涩图插件合二为一
    'hoshino_training',#慎重启用,前往https://github.com/zyujs/hoshino_training查看说明
    #'rss',#适用于Hoshino v2的rss订阅插件,详情https://github.com/zyujs/rss
    'Genshin',#原神系列，其中的genshinuid需要填入你的米游社cookies才能使用
    #'pcravatarguesskiller',#人机猜头像，通常用于群有两个及以上Bot
    #'pcrdescguesskiller',#人机猜角色，通常用于群有两个及以上Bot
    'pcr_calendar',#全服务器通用日历表，关键词为日历
    #'shebot',#插件合集，来源https://github.com/pcrbot/plugins-for-Hoshino,其中的接头需要百度云api
    'weather',#天气插件
    #'snitchgenerator',#需要安装字体，位于XCW\hoshino\hoshino\modules\snitchgenerator\fonts
    #'xcw',#数个插件的混合，需要xcw资源包配合链接：https://pan.baidu.com/s/1tb0skZTs8NSHYZ-Tm3Cs0w 提取码：2333 
    'revgif',#GIF图倒放
    'groupmanager',#群管插件
    #'yocool',#安装yocool
    'pcrjjc',#竞技场背刺推送,更推荐pcrjjc2_xcw
    #'pcrjjc2_xcw',#开启pcrjjc2_xcw前，请前往hoshino_xcw\XCW\Hoshino\hoshino\modules\pcrjjc2_xcw里的account.json,填入一个高等级的公主连结账号（废弃号），"account"填账号，"password"填密码，"admin"填你的QQ号，其余不用管如果是国服的话
    'bilidynamicpush',#B站动态
    'CQTwitter',#rss订阅推特
    'pcr-rank',#自动更新rank
    'pcravatarfind',#找头像
    'shaojo',
}

version = 'hoshino_xcw_1.0'