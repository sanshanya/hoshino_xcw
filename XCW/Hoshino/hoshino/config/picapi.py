# 本文件应该放置于ho的config文件下
# 使用说明？文件位置都放好了，直接根目录解压覆盖就行了，至于命令如你所见在下面自定义就好了
# 然后在HoshinoBot\hoshino\config路径打开_bot_.py文件，找到MODULES_ON的最后添加'picapi'

# 用于存放调用的图片，必须是ho的config中__bot__.py里自己设置的RES_DIR的资源库文件路径下的文件
_PIC_PATH = "C:/XCW/res/img/picc"

#填写触发图片调用的关键词，触发词调用的接口与_PIC_URL中填写的地址顺序对应。可以保持格式自行修改和添加
_PIC_keyword = [
'1号老婆',
'2号老婆',
'3号老婆',
'4号老婆'
]

#出图接口的地址，触发指令与_PIC_keyword中填写的指令对应。可以保持格式自行修改和添加
#如果想要用关键词，从多个接口中随机选出一个接口出图，可以将多个接口地址用“|”连接
#仅支持单纯的打开页面即出图的地址接口，并不支持需要apikey的接口，shebot、acggov-setu不香么？_(:з」∠)_
_PIC_URL = [
'http://myepk.club:2020/?msg=ecy|http://api.mtyqx.cn/api/random.php|http://www.dmoe.cc/random.php|https://www.320nle.com/acggirl/acgurl.php',
'https://api.loli.rocks/mix|https://api.loli.rocks',
'https://img.xjh.me/random_img.php|http://api.iehu.cn/Head.php',
'https://api.ixiaowai.cn/api/api.php|https://api.ixiaowai.cn/mcapi/mcapi.php|http://api.iehu.cn/Image.php|http://106.52.37.243'
]


#以上 所有出现的接口为本人日常搜集目前确认可用的acg插图接口
#在这里为这些提供接口的大佬们报以最衷心的感谢 by阿米娅