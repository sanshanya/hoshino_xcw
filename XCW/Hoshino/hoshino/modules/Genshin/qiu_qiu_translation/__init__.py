from hoshino import Service, priv
from .qiu_qiu_translation import qiu_qiu_word_translation,qiu_qiu_phrase_translation


sv_help = '''
- [丘丘一下] 丘丘语变中文
- [丘丘词典] 查询单词含义
'''.strip()

sv = Service(
    name = '原神翻译',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    bundle = '原神', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助原神翻译"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help) 

suffix = "\n※ 这个插件只能从丘丘语翻译为中文，不能反向翻译"



@sv.on_prefix("丘丘一下")
async def qiu_qiu(bot, ev):
    txt = ev.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_word_translation(txt)
    mes += suffix
    await bot.send(ev, mes,at_sender=True)



@sv.on_prefix("丘丘词典")
async def qiu_qiu(bot, ev):
    txt = ev.message.extract_plain_text().strip().lower()
    if txt == "":
        return
    mes = qiu_qiu_phrase_translation(txt)
    mes += suffix
    await bot.send(ev, mes,at_sender=True)







