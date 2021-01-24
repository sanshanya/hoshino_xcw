import time
from hoshino import Service, priv, aiorequests
from nonebot import MessageSegment

BASE_URL = 'https://api-cn.faceplusplus.com/imagepp/v1/mergeface'

params = {
    'api_key': '',  # 申请的 API Key 填这里
    'api_secret': '',  # 申请的 API Secret 填这里
    'merge_rate': 50,  # 融合比例，范围 [0,100]。数字越大融合结果包含越多融合图特征 默认值为50
    'feature_rate': 80  # 五官融合比例，范围 [0,100]。主要调节融合结果图中人像五官相对位置，数字越小融合图中人像五官相对更集中 。 默认值为45
}

tm_url = ['template_url', 'merge_url']

sv_help = '''
无说明
'''.strip()

sv = Service(
    name = '换脸',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.SUPERUSER, #管理权限
    visible = False, #False隐藏
    enable_on_default = False, #是否默认启用
    bundle = '娱乐', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助换脸"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)



wait_list = {}


@sv.on_fullmatch('换脸')
async def mergeface(bot, ev):
    await bot.send(ev, '请发送第一张图片')
    wait_list[ev['user_id']] = []


@sv.on_message('group')
async def target_img_get(bot, ev):
    user_id = ev['user_id']
    if user_id not in wait_list.keys():
        return

    for msg in ev['message']:
        if msg['type'] == 'image':
            wait_list[user_id].append(msg['data']['url'])
        else:
            await bot.send(ev, '要发图片哦~')
    if len(wait_list[user_id]) == 1:
        await bot.send(ev, '还需要第二张图')
    if len(wait_list[user_id]) == 2:
        await bot.send(ev, '请稍等。正在合成')
        await request_mergeface(dict(zip(tm_url, wait_list[user_id])), bot, ev)
        del wait_list[ev['user_id']]


async def request_mergeface(target, bot, ev):
    try:
        response = await aiorequests.post(BASE_URL, data=dict(params, **target), timeout=30)
        info = await response.json()
        error_message = info.get('error_message')
        if error_message:
            print(error_message)
            if 'CONCURRENCY_LIMIT_EXCEEDED' in error_message:  # 判断是否是QPS
                time.sleep(1)
                await request_mergeface(target, bot, ev)
            else:
                await bot.send(ev, get_error_msg(error_message))
            return
        await bot.send(ev, MessageSegment.image('base64://' + info['result']))
    except:
        await bot.send(ev, '呜呜呜网络视乎出现了一点问题呢，请稍后再试试吧.')


def get_error_msg(error_message):
    index = '一' if 'template_url' in error_message else '二'
    if 'NO_FACE_FOUND' in error_message:
        return f'第{index}张图木有检测到人脸'
    if 'IMAGE_ERROR_UNSUPPORTED_FORMAT' in error_message:
        return f'第{index}张图有可能不是一个图像文件、或有数据破损。'
    if 'INVALID_IMAGE_SIZE' in error_message:
        return f'第{index}张图像像素尺寸太大或太小。'
    if 'INVALID_IMAGE_URL' in error_message:
        return f'第{index}张图片错误或者无效。'
    if 'IMAGE_FILE_TOO_LARGE' in error_message:
        return f'第{index}张图像文件太大。'
    if 'BAD_FACE' in error_message:
        return f'图片人脸不符合要求。'
    if 'INVALID_RECTANGLE' in error_message:
        return f'第{index}张人脸框格式不符合要求，或者人脸框位于图片外。'
    if 'IMAGE_DOWNLOAD_TIMEOUT' in error_message:
        return f'第{index}张图片超时。'
    # 通用
    if 'AUTHENTICATION_ERROR' in error_message:
        return f'api_key和api_secret不匹配。'
    if 'AUTHORIZATION_ERROR' in error_message:
        return f'api_key没有调用本API的权限，具体原因为：用户自己禁止该api_key调用、管理员禁止该api_key调用、由于账户余额不足禁止调用'
    if 'INTERNAL_ERROR' in error_message:
        return f'服务器内部错误，当此类错误发生时请再次请求，如果持续出现此类错误，请及时联系技术支持团队。'
