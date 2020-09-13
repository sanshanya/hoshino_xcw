"""这是一份实例配置文件

将其修改为你需要的配置，并将文件夹config_example重命名为config
"""

# hoshino监听的端口与ip
PORT = 9222
HOST = '0.0.0.0'      # 本地部署使用此条配置（QQ客户端和bot端运行在同一台计算机）
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）

DEBUG = False           # 调试模式

SUPERUSERS = [1057069677]    # 填写超级用户的QQ号，可填多个用半角逗号","隔开
PYS ={2212276520}            #高级权限用户的QQ号


#接下来是hoshino_xcw的专用配置，如果使用hoshino_xcw整合包请一定要修改

NICKNAME = r'镜华|小仓唯|露娜|at,qq=2380695163'           # 设置bot的昵称，at，qq=xxxxxxxx处为bot的QQ号,呼叫昵称等同@bot
IP = '333.33.33.3'                                      #修改为你的服务器ip
public_address = '333.33.33.3:9222'                     #修改为你的服务器ip+端口
IMAGE_PATH = "C:/XCW/miraiGO/data/images"                 #MiraiGO用这条

#hoshino_xcw的专用配置结束

COMMAND_START = {''}    # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()     # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# 发送图片的协议
# 可选 http, file, base64
# 当QQ客户端与bot端不在同一台计算机时，可用http协议
RES_PROTOCOL = 'file'
# 资源库文件夹，需可读可写，windows下注意反斜杠转义
RES_DIR = "C:/XCW/res/"
# 使用http协议时需填写，原则上该url应指向RES_DIR目录
RES_URL = 'http://127.0.0.1:5000/static/'


# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
# 切忌一次性开启多个
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
    # 'twitter',#推特订阅，需要apikey
    'yobot',#yobot会战功能
    'hourcallyao',#买药提醒
    #'shebot_old',#色图功能，需要apikey——mirai需要按说明适配,本版本shebot可以直接私聊,请勿和下方版本同时开启,下方有集成优化版
    'reload',#重启，暂时不知是否能生效
    'longwang',#迫害龙王功能
    'tarot',#塔罗牌，需要修改路径
    'flac',#搜无损音乐，暂时无用  
    'shitu',#识图功能需要apikey
    'shifan',#识别番剧
    'ClanBattleReport',#会战报告生成，需要修改路径
    #'setu_acggov',#搜图，需要apikey，mirai需要按说明适配
    'bot_manager_web',#新版webmanage
    #'voiceguess',#猜语音,Mirai后续版本可用
    #'eclanrank',#会战排名提醒，定时播报，会战时启用
    #'tencent_ai_reply',#需要apikey，用前修改概率
    #'QA',#问答功能,下方有集成优化版
    'hiumsentences',#网抑云语录
    'generator',#营销文生成等五个小功能
    'ontree_scheduler',#挂树优化提醒
    #'eqa',#问答功能2
    'russian',#俄罗斯轮盘赌
    'explosion',#每天一发惠惠
    'boxcolle',#BOX查询
    'timeline',#轴上传
    'picapi',#自定义拉取图片
    'aircon',#群空调
    #'authMS',#群授权,目前存在一定问题,自行通过报错解决
    #'bilisearchspider',#b站订阅
    'pcravatarguess',#图片猜角色
    'pcrdescguess',#通过角色描述猜角色,需要设置go-cqhttp的心跳间隔,推荐3
    #'shebot',##集合了许多插件,请勿和shebot及QA同时开启
    #'nmsl',#抽象抽象抽抽抽像像像
    #'clanbattle_report',#远程api生成会战报告
    'baidupan',#百度盘解析
    'calendar',#查看日程表,实用的全服务器可用的功能
    'meme_web',#memegenerator的web化,勿同时开启
    #'pcrmiddaymusic',#公主连结午间音乐
    #'image_generate',#取代原image
    'music',#点歌插件
    'pcrmemorygames',#公主连结记忆小游戏
    'epixiv',#需要pixiv站账号
    'emergeface',#换脸插件,需要apikey
    'eclanblack',#兰德索尔黑名单
}
