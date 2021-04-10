import os
from hoshino import Service,priv
from hoshino.priv import *
from hoshino import aiorequests
from os import path
import json
from nonebot import scheduler
from PIL import Image

sv_help = '''
- [日/台/陆rank] rank推荐
- [更新rank源缓存]
'''.strip()

sv = Service(
    name = 'rank表',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '查询', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助rank表"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

server_addr = "https://pcresource.coldthunder11.com/rank/"
resize_pic = False
config = None

async def load_config():
    global config
    global server_addr
    config_path = path.join(path.dirname(__file__),"config.json")
    with open(config_path,"r",encoding="utf8")as fp:
        config = json.load(fp)
        server_addr = config['upstream']
        resize_pic = config['resize_pic']
    if not path.exists(path.join(path.abspath(path.dirname(__file__)),"cache")):
        os.mkdir(path.join(path.abspath(path.dirname(__file__)),"cache"))
    if not path.exists(path.join(path.abspath(path.dirname(__file__)),"cache","pic")):
        os.mkdir(path.join(path.abspath(path.dirname(__file__)),"cache","pic"))
        await update_cache()

def save_config():
    config_path = path.join(path.dirname(__file__),"config.json")
    with open(config_path,'r+',encoding='utf8')as fp:
        fp.seek(0)
        fp.truncate()
        str = json.dumps(config,indent=4,ensure_ascii=False)
        fp.write(str)

async def download_rank_pic(url):
    sv.logger.info(f"正在下载{url}")
    resp = await aiorequests.head(url)
    content_length = int(resp.headers["Content-Length"])
    sv.logger.info(f"块大小{str(content_length)}")
    #分割200kb下载
    block_size = 1024*200
    range_list = []
    current_start_bytes = 0
    while True:
        if current_start_bytes + block_size >= content_length:
            range_list.append(f"{str(current_start_bytes)}-{str(content_length)}")
            break
        range_list.append(f"{str(current_start_bytes)}-{str(current_start_bytes + block_size)}")
        current_start_bytes += block_size + 1
    pic_bytes_list = []
    for block in range_list:
        sv.logger.info(f"正在下载块{block}")
        headers = {"Range":f"bytes={block}"}
        resp = await aiorequests.get(url,headers = headers)
        res_content = await resp.content
        pic_bytes_list.append(res_content)
    return b"".join(pic_bytes_list)

async def update_rank_pic_cache(force_update:bool):
    config_names = ["cn","tw","jp"]
    for conf_name in config_names:
        config_path = path.join(path.dirname(__file__),"cache",f"{conf_name}.json")
        with open(config_path,"r",encoding="utf8")as fp:
            rank_config = json.load(fp)
        for img_name in rank_config["files"]:
            if not force_update:
                if path.exists(path.join(path.abspath(path.dirname(__file__)),"cache","pic",f"{conf_name}_{img_name}")):
                    continue
            rank_img_url = f"{server_addr}{config['source'][conf_name]['channel']}/{config['source'][conf_name]['route']}/{img_name}"
            img_content = await download_rank_pic(rank_img_url)
            with open(path.join(path.abspath(path.dirname(__file__)),"cache","pic",f"{conf_name}_{img_name}"),"ab")as fp:
                fp.seek(0)
                fp.truncate()
                fp.write(img_content)

async def update_cache(force_update:bool=False):
    sv.logger.info("正在更新Rank表缓存")
    config_names = ["cn","tw","jp"]
    for conf_name in config_names:
        resp = await aiorequests.get(f"{server_addr}{config['source'][conf_name]['channel']}/{config['source'][conf_name]['route']}/config.json")
        res = await resp.text
        cache_path = path.join(path.abspath(path.dirname(__file__)),"cache",f"{conf_name}.json")
        with open(cache_path,"a",encoding="utf8")as fp:
            fp.seek(0)
            fp.truncate()
            fp.write(res)
    await update_rank_pic_cache(force_update)
    sv.logger.info("Rank表缓存更新完毕")

@sv.on_rex(r"^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$")
async def rank_sheet(bot, ev):
    if config == None:
        await load_config()
    match = ev["match"]
    is_jp = match.group(2) == "日"
    is_tw = match.group(2) == "台"
    is_cn = match.group(2) and match.group(2) in "国陆b"
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev, "\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*陆rank表", at_sender=True)
        return
    msg = []
    msg.append("\n")
    if is_jp:
        rank_config_path = path.join(path.abspath(path.dirname(__file__)),"cache","jp.json")
        rank_config = None
        with open(rank_config_path,"r",encoding="utf8")as fp:
            rank_config = json.load(fp)
        rank_imgs = []
        for img_name in rank_config["files"]:
            rank_imgs.append(f'file:///{path.join(path.dirname(__file__),"cache","pic",f"jp_{img_name}")}')
        msg.append(rank_config["notice"])
        pos = match.group(3)
        if not pos or "前" in pos:
            msg.append(f"[CQ:image,file={rank_imgs[0]}]")
        if not pos or "中" in pos:
            msg.append(f"[CQ:image,file={rank_imgs[1]}]")
        if not pos or "后" in pos:
            msg.append(f"[CQ:image,file={rank_imgs[2]}]")
        await bot.send(ev, "".join(msg), at_sender=True)
    elif is_tw:
        rank_config_path = path.join(path.abspath(path.dirname(__file__)),"cache","tw.json")
        rank_config = None
        with open(rank_config_path,"r",encoding="utf8")as fp:
            rank_config = json.load(fp)
        rank_imgs = []
        for img_name in rank_config["files"]:
            rank_imgs.append(f'file:///{path.join(path.dirname(__file__),"cache","pic",f"tw_{img_name}")}')
        msg.append(rank_config["notice"])
        for rank_img in rank_imgs:
            msg.append(f"[CQ:image,file={rank_img}]")
        await bot.send(ev, "".join(msg), at_sender=True)
    elif is_cn:
        rank_config_path = path.join(path.abspath(path.dirname(__file__)),"cache","cn.json")
        rank_config = None
        with open(rank_config_path,"r",encoding="utf8")as fp:
            rank_config = json.load(fp)
        rank_imgs = []
        for img_name in rank_config["files"]:
            rank_imgs.append(f'file:///{path.join(path.dirname(__file__),"cache","pic",f"cn_{img_name}")}')
        msg.append(rank_config["notice"])
        for rank_img in rank_imgs:
            msg.append(f"[CQ:image,file={rank_img}]")
        await bot.send(ev, "".join(msg), at_sender=True)

@sv.on_fullmatch("查看当前rank更新源")
async def show_current_rank_source(bot, ev):
    if config == None:
        await load_config()
    if not check_priv(ev, SUPERUSER):
        await bot.send(ev, "仅有SUPERUSER可以使用本功能")
    msg = []
    msg.append("\n")
    msg.append("国服:\n")
    msg.append(config["source"]["cn"]["name"])
    msg.append("   ")
    if config["source"]["cn"]["channel"] == "stable":
        msg.append("稳定源")
    elif config["source"]["cn"]["channel"] == "auto_update":
        msg.append("自动更新源")
    else:
        msg.append(config["source"]["cn"]["channel"])
    msg.append("\n台服:\n")
    msg.append(config["source"]["tw"]["name"])
    msg.append("   ")
    if config["source"]["tw"]["channel"] == "stable":
        msg.append("稳定源")
    elif config["source"]["tw"]["channel"] == "auto_update":
        msg.append("自动更新源")
    else:
        msg.append(config["source"]["tw"]["channel"])
    msg.append("\n日服:\n")
    msg.append(config["source"]["jp"]["name"])
    msg.append("   ")
    if config["source"]["jp"]["channel"] == "stable":
        msg.append("稳定源")
    elif config["source"]["jp"]["channel"] == "auto_update":
        msg.append("自动更新源")
    else:
        msg.append(config["source"]["jp"]["channel"])
    await bot.send(ev, "".join(msg), at_sender=True)

@sv.on_fullmatch("查看全部rank更新源")
async def show_all_rank_source(bot, ev):
    if config == None:
        await load_config()
    if not check_priv(ev, SUPERUSER):
        await bot.send(ev, "仅有SUPERUSER可以使用本功能")
    resp = await aiorequests.get(server_addr+"route.json")
    res = await resp.json()
    msg = []
    msg.append("\n")
    msg.append("稳定源：\n国服:\n")
    for uo in res["ranks"]["channels"]["stable"]["cn"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n台服:\n") 
    for uo in res["ranks"]["channels"]["stable"]["tw"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n日服:\n") 
    for uo in res["ranks"]["channels"]["stable"]["jp"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n自动更新源：\n国服:\n")
    for uo in res["ranks"]["channels"]["auto_update"]["cn"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n台服:\n") 
    for uo in res["ranks"]["channels"]["auto_update"]["tw"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n日服:\n") 
    for uo in res["ranks"]["channels"]["auto_update"]["jp"]:
        msg.append(uo["name"])
        msg.append("   ")
    msg.append("\n如需修改更新源，请使用命令[设置rank更新源 国/台/日 稳定/自动更新 源名称]") 
    await bot.send(ev, "".join(msg), at_sender=True)

@sv.on_rex(r'^设置rank更新源 (.{0,5}) (.{0,10}) (.{0,20})$')
async def change_rank_source(bot, ev):
    if config == None:
        await load_config()
    if not check_priv(ev, SUPERUSER):
        await bot.send(ev, "仅有SUPERUSER可以使用本功能")
    robj = ev['match']
    server = robj.group(1)
    channel = robj.group(2)
    name = robj.group(3)
    if server == "国":
        server = "cn"
    elif server == "台":
        server = "tw"
    elif server == "日":
        server = "jp"
    else :
        await bot.send(ev, "请选择正确的服务器（国/台/日）", at_sender=True)
        return
    if channel == "稳定":
        channel = "stable"
    elif channel == "自动更新":
        channel = "auto_update"
    else :
        await bot.send(ev, "请选择正确的频道（稳定/自动更新）", at_sender=True)
        return
    resp = await aiorequests.get(server_addr+"route.json")
    res = await resp.json()
    has_name = False
    source_jo = None
    for uo in res["ranks"]["channels"][channel][server]:
        if uo["name"].upper() == name.upper():
            has_name = True
            source_jo = uo
            break
    if not has_name:
        await bot.send(ev, "请输入正确的源名称", at_sender=True)
        return
    config["source"][server]["name"] = source_jo["name"]
    config["source"][server]["channel"] = channel
    config["source"][server]["route"] = source_jo["route"]
    save_config()
    await update_cache(True)
    await bot.send(ev, "更新源设置成功", at_sender=True)

@sv.on_fullmatch("更新rank表缓存")
async def update_rank_cache(bot, ev):
    if config == None:
        await load_config()
    if not check_priv(ev, SUPERUSER):
        await bot.send(ev, "仅有SUPERUSER可以使用本功能")
    await update_cache()
    await bot.send(ev, "更新成功")

@scheduler.scheduled_job('cron', hour='17', minute='06')
async def schedule_update_rank_cache():
    if config == None:
        await load_config()
    await update_cache()
