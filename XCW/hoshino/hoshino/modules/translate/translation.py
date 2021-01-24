import json
import requests
from hoshino import Service, priv
from hoshino.typing import *

sv_help = '''
- [翻译 XXX] 通过有道词典进行翻译
'''.strip()

sv = Service(
    name = '翻译',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助翻译"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)
    

Headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

@sv.on_command('translate', aliases=('翻译', '翻譯', '翻訳'), only_to_me=False)
async def translation(session: CommandSession):
    sentence = session.get('sentence', prompt="你想翻译什么呢?")
    res = await fff(sentence)
    if res:
        await session.send(res)
    else:
        await session.send("[ERROR]Not found translate_Info")
    

@translation.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        if stripped_arg:
            session.state['sentence'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('要翻译的内容称不能为空呢，请重新输入')

    session.state[session.current_key] = stripped_arg


def translate(word):
    # 有道词典 api
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # 传输的参数，其中 i 为需要翻译的内容
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "true"
    }
    # key 这个字典为发送给有道词典服务器的内容
    response = requests.post(url, data=key)
    # 判断服务器是否相应成功
    if response.status_code == 200:
        # 然后相应的结果
        return response.text
    else:
        return "Failed!"


def get_reuslt(repsonse):
    # 通过 json.loads 把返回的结果加载成 json 格式
    result = json.loads(repsonse)
    return result['translateResult'][0][0]['tgt']


async def fff(word: str) -> str:
    list_trans = translate(word)
    # 将json数据转换为dict数据
    x = get_reuslt(list_trans)
    return f'>有道:\n{x}'