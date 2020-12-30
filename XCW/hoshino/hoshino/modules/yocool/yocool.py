# -*- coding: utf-8 -*-
import hoshino, os, json, shutil, zipfile, asyncio, glob
from nonebot import on_command, get_bot, scheduler
from hoshino import aiorequests, util

# 自动更新结果是否通知主人
NOTICE = False

try:
    config = hoshino.config.yocool.setup_config
except:
    hoshino.logger.error('not found config of yocoolconsole')

try:
    path  = config.path
except:
    path = os.path.dirname(__file__)

try:
    yobot_path  = config.path
except:
    yobot_path = './hoshino/modules/yobot/yobot/'

yobot_themes_path = os.path.join(yobot_path, 'src', 'client', 'public')
yocool_themes_path = os.path.join(path, 'public')
backup_themes_path = os.path.join(path, 'backup', 'public')
current_info_path = os.path.join(path, 'yocool_info.json')

themes_0 = '主题未设置'
themes_PA = 'PrincessAdventure'
themes_CL = 'CoolLite'

newest_info_url = 'https://yocool.pcrlink.cn/yocool_info.json'
git_yocool_releases = 'https://hub.fastgit.org/A-kirami/YoCool/releases/download/'

THEMES_NAME_TIP = '请选择需要切换的主题！\n1. 公主冒险 PrincessAdventure\n2. 轻酷 CoolLite\n*切换主题+序号或名称即可'


def get_install_state() -> int:
    '''
    检查安装状态
    '''
    hoshino.logger.info('检查YoCool安装状态')
    if os.path.exists(current_info_path):
        with open(current_info_path, 'r', encoding='utf-8') as lv:
            lvj = json.load(lv)
            current_tms = int(lvj["Install"])
    else:
        current_tms = 0
    return current_tms


def get_current_ver() -> int:
    '''
    获取本地版本号
    '''
    if os.path.exists(current_info_path):
        with open(current_info_path, 'r', encoding='utf-8') as lv:
            lvj = json.load(lv)
            current_ver = int(lvj["ver"])
            current_tag = str(lvj["Version"])
    else:
        current_ver = 0
    hoshino.logger.info(f'本地YoCool版本：YoCool-{current_tag}')
    return current_ver


def get_current_tms() -> int:
    '''
    获取本地安装主题
    '''
    if os.path.exists(current_info_path):
        with open(current_info_path, 'r', encoding='utf-8') as lv:
            lvj = json.load(lv)
            current_tms = int(lvj["Themes"])
    else:
        current_tms = 0
    return current_tms


def get_yocool_themes(select) -> str:
    '''
    获取主题对应名称
    '''
    if select == 1:
        themes = themes_PA
    elif select == 2:
        themes = themes_CL
    else:
        themes = themes_0
    return themes


async def get_newest_ver() -> str:
    '''
    获取最新版本号与更新日志
    '''
    newest_yocool_ver = await aiorequests.get(url=newest_info_url, timeout=10)
    if newest_yocool_ver.status_code != 200:
        hoshino.logger.error(f'获取最新YoCool版本时发生错误{newest_yocool_ver.status_code}')
        return newest_yocool_ver.status_code, 0, 0
    newest_yocool_ver_json = await newest_yocool_ver.json()
    newest_ver = int(newest_yocool_ver_json["ver"])
    newest_tag = str(newest_yocool_ver_json["Version"])
    newest_udn = str(newest_yocool_ver_json["UpdateNote"])
    hoshino.logger.info(f'当前最新YoCool版本：YoCool-{newest_tag}')
    return newest_ver, newest_tag, newest_udn


def update_current_ver(ver,Version,UpdateNote) -> None:
    '''
    更新本地信息
    '''
    with open(current_info_path, 'r', encoding='utf-8') as f:
        current_updata_json = json.load(f)
    current_updata_json['ver'] = ver
    current_updata_json['Version'] = Version
    current_updata_json['UpdateNote'] = UpdateNote
    current_updata_json['Install'] = 1
    with open(current_info_path, 'w+', encoding='utf-8') as f:
        json.dump(current_updata_json, f, indent=4, ensure_ascii=False)
    hoshino.logger.info(f'更新本地YoCool信息文件')


async def get_yocool_file(newest_tag,themes):
    '''
    获取yocool文件
    '''
    hoshino.logger.info(f'开始下载YoCool主题{themes}')
    download_url = git_yocool_releases + newest_tag + '/YoCool-'+ newest_tag + '-' + themes + '-plugin.zip'
    response =  await aiorequests.get(download_url, stream=True, timeout=20)
    status_code = response.status_code
    if status_code != 200:
        hoshino.logger.error(f'下载YoCool最新版本时发生错误{status_code}')
        return {}
    content = await response.content
    with open(path + '/public.zip', 'wb') as f:
        f.write(content)
    hoshino.logger.info('开始解压缩主题文件')
    zip_files = [file for file in os.listdir(path) if file.endswith('.zip')]
    for zfile in zip_files:
        f = zipfile.ZipFile(os.path.join(path, zfile),'r')
        for file in f.namelist():
            f.extract(file,os.path.join(path, zfile[:-4]))
    hoshino.logger.info('主题文件解压完成')
    hoshino.logger.info('主题文件准备完毕！')


async def update_yocool(force=False) -> str:
    '''
    从git下载releases安装
    指定force为true, 则不会比较本地版本号是否最新
    '''
    # 获取最新版本编码，版本号,更新日志
    newest_ver, newest_tag, newest_udn = await get_newest_ver()
    if newest_ver < 1000:
        hoshino.error(f'获取YoCool版本时发生错误{newest_ver}')
        return newest_ver, newest_tag, newest_udn

    # 比较本地版本
    current_ver = get_current_ver()
    if force:
        # 指定强制更新
        current_ver = 0
    if newest_ver <= current_ver:
        newest_ver = 0
        return newest_ver, newest_tag, newest_udn

    # 获取本地设置主题
    hoshino.logger.info('检查本地主题配置')
    select = get_current_tms()
    themes = get_yocool_themes(select)
    hoshino.logger.info(f'本地主题当前配置：{themes}')

    # 下载文件
    getcode = await get_yocool_file(newest_tag,themes)
    if getcode == {}:
        hoshino.logger.error(f'下载YoCool文件时发生错误')
        return -1, newest_tag, newest_udn

    # 旧文件备份文件
    ins = get_install_state()
    if ins == 0:
        hoshino.logger.info('正在备份yobot原生主题文件')
        shutil.move(yobot_themes_path,backup_themes_path)

    # 写入新文件
    hoshino.logger.info('正在写入YoCool主题文件')
    shutil.move(yocool_themes_path,yobot_themes_path)
    hoshino.logger.info('YoCool安装完成！')

    # 删除压缩包
    hoshino.logger.info('清理无用文件')
    for infile in glob.glob(os.path.join(path, '*.zip')):
        os.remove(infile)

    # 覆盖本地版本号
    hoshino.logger.info(f'更新版本信息：YoCool-{newest_tag}')
    update_current_ver(newest_ver, newest_tag, newest_udn)
    return newest_ver, newest_tag, newest_udn


async def uninstall_yocool(force=False) -> str:
    '''
    卸载YoCool
    指定force为true, 则不会检查是否安装
    '''
    ins = get_install_state()
    if force:
        ins = 1
    if ins == 0:
        return 0

    hoshino.logger.info('正在验证YoCool配置完整性')
    if not os.path.exists(yobot_themes_path) or not os.path.exists(backup_themes_path):
        return 1
    hoshino.logger.info('正在移除YoCool文件')
    try:
        shutil.rmtree(yobot_themes_path)
    except:
        return 2
    await asyncio.sleep(5)
    hoshino.logger.info('开始从备份恢复')
    try:
        shutil.move(backup_themes_path,yobot_themes_path)
    except:
        return 3
    await asyncio.sleep(5)
    try:
        os.rmdir('./hoshino/modules/yocool/backup')
    except:
        return 4
    hoshino.logger.info('YoCool卸载完成！')
    with open(current_info_path, 'r', encoding='utf-8') as f:
        current_updata_json = json.load(f)
    current_updata_json['Install'] = 0
    current_updata_json['ver'] = 0
    with open(current_info_path, 'w+', encoding='utf-8') as f:
        json.dump(current_updata_json, f, indent=4, ensure_ascii=False)
    return 5


@on_command('一键安装', aliases=('快速安装', '一键YoCool', '一键yocool', '一键YOCOOL'), only_to_me=True)
async def one_key_yocool(session):
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    if os.path.exists(backup_themes_path):
        await session.finish('您已经安装过了，如需更新请发送【更新YoCool】')
    name = util.normalize_str(session.current_arg_text)
    if not name:
        select = 1
    elif name in ('公主冒险', 'PrincessAdventure', '1'):
        select = 1
    elif name in ('轻酷', 'CoolLite', '2'):
        select = 2
    else:
        await session.finish(f'没有找到主题{name}，请检查输入后再试')
    hoshino.logger.info('正在进行安装前初始化')
    if os.path.exists(current_info_path):
        for infile in glob.glob(os.path.join(path, '*.json')):
            os.remove(infile)
    newest_yocool_ver = await aiorequests.get(url=newest_info_url)
    if newest_yocool_ver.status_code != 200:
        hoshino.logger.error(f'获取YoCool版本信息时发生错误{newest_yocool_ver.status_code}')
        await session.send(f'获取YoCool版本信息时发生错误{newest_yocool_ver.status_code}')
    yocool_info_json = await newest_yocool_ver.json()
    yocool_info_json['Themes'] = select
    with open(current_info_path, 'w+', encoding='utf-8') as f:
        json.dump(yocool_info_json, f, indent=4, ensure_ascii=False)
    themes = get_yocool_themes(select)
    await session.send(f'YoCool初始化完成，准备使用{themes}主题进行安装，安装需要一定时间，请耐心等待……')
    status, version, updatenote = await update_yocool(force=True)
    if status == 0:
        for infile in glob.glob(os.path.join(path, '*.json')):
            os.remove(infile)
        await session.finish('本地版本信息异常！请重新发送指令再试！')
    elif status < 1000:
        await session.finish(f'发生错误{status}')
    else:
        await session.finish(f'一键安装已完成！\n当前YoCool版本：YoCool-{version}\n使用主题：{themes}\n更新日志：\n{updatenote}\n*电脑端请使用Ctrl+F5强制刷新浏览器缓存，移动端请在浏览器设置中清除缓存')


@on_command('切换主题', aliases=('更换主题', '变更主题', '修改主题'), only_to_me=True)
async def set_yocool_themes(session):
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    if not os.path.exists(current_info_path):
        await session.send('没有找到YoCool信息配置文件，请发送【安装YoCool】后再试')
    name = util.normalize_str(session.current_arg_text)
    if not name:
        await session.finish(THEMES_NAME_TIP, at_sender=True)
    elif name in ('公主冒险', 'PrincessAdventure', '1'):
        select = 1
    elif name in ('轻酷', 'CoolLite', '2'):
        select = 2
    else:
        await session.finish(f'没有找到主题{name}，请检查输入后再试')
    with open(current_info_path, 'r', encoding='utf-8') as f:
        current_updata_json = json.load(f)
    current_updata_json['Themes'] = select
    with open(current_info_path, 'w+', encoding='utf-8') as f:
        json.dump(current_updata_json, f, indent=4, ensure_ascii=False)
    themes = get_yocool_themes(select)
    hoshino.logger.info(f'设置YoCool主题为{themes}')
    await session.send('开始切换主题，需要一定时间，请耐心等待……')
    shutil.rmtree(yobot_themes_path)
    await asyncio.sleep(5)
    await update_yocool(force=True)
    await session.finish(f'YoCool主题已切换为{themes}')


@on_command('更新YoCool', aliases=('更新yocool', '更新YOCOOL', '升级YoCool', '升级yocool', '升级YOCOOL'), only_to_me=True)
async def update_yocool_chat(session):
    '''
    手动更新
    '''
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    ins = get_install_state()
    if ins == 0:
        await session.finish('当前未安装YoCool')
    hoshino.logger.info('开始检查YoCool更新')
    await session.send('开始进行YoCool更新，需要一定时间，请耐心等待……')
    try:
        status, version, updatenote = await update_yocool()
    except:
        await session.send('更新异常中断，请排查问题后再次尝试')
    if status == 0:
        await session.finish('已是最新版本, 仍要更新YoCool请使用【强制更新YoCool】命令')
    elif status < 1000:
        await session.finish(f'发生错误{status}')
    else:
        await session.finish(f'更新完成！\n当前YoCool版本：YoCool-{version}\n更新日志：\n{updatenote}\n*电脑端请使用Ctrl+F5强制刷新浏览器缓存，移动端请在浏览器设置中清除缓存')


@on_command('强制更新YoCool', aliases=('强制更新yocool', '强制更新YOCOOL', '强制升级YoCool', '强制升级yocool', '强制升级YOCOOL'), only_to_me=True)
async def update_yocool_force_chat(session):
    '''
    强制更新
    '''
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    hoshino.logger.info('开始检查YoCool更新')
    ins = get_install_state()
    if ins == 0:
        await session.finish('当前未安装YoCool')
    await session.send('开始进行YoCool更新，需要一定时间，请耐心等待……')
    try:
        status, version, updatenote = await update_yocool(force=True)
    except:
        await session.send('更新异常中断，请排查问题后再次尝试')
    if status == 0:
        await session.finish(f'状态{status}')
    elif status < 1000:
        await session.finish(f'发生错误{status}')
    else:
        await session.finish(f'更新完成！\n当前YoCool版本：YoCool-{version}\n更新日志：\n{updatenote}\n*电脑端请使用Ctrl+F5强制刷新浏览器缓存，移动端请在浏览器设置中清除缓存')


@on_command('卸载YoCool', aliases=('卸载yocool', '卸载YOCOOL'), only_to_me=True)
async def uninstall_yocool_chat(session):
    '''
    卸载
    '''
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    await session.send('YoCool卸载开始，需要一定时间，请耐心等待……')
    yocode = await uninstall_yocool()
    if yocode == 0:
        await session.finish('尚未安装YoCool，无法操作')
    elif yocode ==1:
        await session.finish('YoCool完整性验证未通过，没有找到YoCool文件或备份文件夹')
    elif yocode ==2:
        await session.finish('移除YoCool文件出错，请手动卸载')
    elif yocode ==3:
        await session.finish('恢复原生主题出错，请手动恢复')
    elif yocode ==4:
        await session.finish('清理残留出错，请手动删除backup文件夹')
    else:
        await session.finish('YoCool卸载完成！')

@on_command('强制卸载YoCool', aliases=('强制卸载yocool', '强制卸载YOCOOL'), only_to_me=True)
async def uninstall_yocool_force_chat(session):
    '''
    强制卸载
    '''
    uid = session.event.user_id
    if uid not in hoshino.config.SUPERUSERS:
        return
    await session.send('YoCool强制卸载开始，需要一定时间，请耐心等待……')
    yocode = await uninstall_yocool(force=True)
    if yocode == 0:
        await session.finish('尚未安装YoCool，无法操作')
    elif yocode ==1:
        await session.finish('YoCool完整性验证未通过，没有找到YoCool文件或备份文件夹')
    elif yocode ==2:
        await session.finish('移除YoCool文件出错，请手动卸载')
    elif yocode ==3:
        await session.finish('恢复原生主题出错，请手动恢复')
    elif yocode ==4:
        await session.finish('清理残留出错，请手动删除backup文件夹')
    else:
        await session.finish('YoCool卸载完成！')


# 每周检查一次，自动进行更新
@scheduler.scheduled_job('cron',day_of_week='1', hour=4, minute=40)
async def update_yocool_sdj():
    bot = get_bot()
    master_id = hoshino.config.SUPERUSERS[0]

    self_ids = bot._wsr_api_clients.keys()
    sid = self_ids[0]

    ins = get_install_state()
    if ins == 0:
        return
    if not os.path.exists(current_info_path):
        newest_yocool_ver = await aiorequests.get(url=newest_info_url)
        if newest_yocool_ver.status_code != 200:
            hoshino.logger.error(f'获取YoCool版本信息时发生错误{newest_yocool_ver.status_code}')
        yocool_info_json = await newest_yocool_ver.json()
        yocool_info_json['Themes'] = 1
        with open(current_info_path, 'w+', encoding='utf-8') as f:
            json.dump(yocool_info_json, f, indent=4, ensure_ascii=False)
    status, version, UpdateNote = await update_yocool()
    if status == 0:
        return
    elif status < 1000 and NOTICE:
        msg = f'自动更新YoCool版本时发生错误{status}'
        await bot.send_private_msg(seld_id=sid, user_id=master_id, message=msg)
    elif NOTICE:
        msg = f'已自动更新YoCool版本\n当前YoCool版本：YoCool-{version}\n本次更新内容：\n{UpdateNote}\n*电脑端请使用Ctrl+F5强制刷新浏览器缓存，移动端请在浏览器设置中清除缓存'
        await bot.send_private_msg(seld_id=sid, user_id=master_id, message=msg)
