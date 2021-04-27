from hoshino import Service, priv, config
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)


TOP_MANUAL2 = f'''
当前版本{config.version}
查看帮助前往
www.xcwbot.top/help/
'''.strip()

TOP_MANUAL3 = '''
※本部分仅群管及以上权限有效
※控制功能开关:
- [开启 XXX] （有空格）
- [禁用 XXX] （有空格）
XXX为功能名
※本群功能开关总览:
- [lssv]
'''.strip()



def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for sv in service_list:
        if sv.visible:
            manual.append(f"|{'○' if sv.check_enabled(gid) else '×'}| {sv.name}")
    return '\n'.join(manual)

def gen_bundle_manual_all(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for sv in service_list:
        if sv.visible:
            spit_line = '=' * max(0, 18 - len(sv.name))
            manual.append(f"|{'○' if sv.check_enabled(gid) else '×'}| {sv.name} {spit_line}")
            if sv.help:
                manual.append(sv.help)
    return '\n'.join(manual)

@sv.on_prefix(('help', '帮助', '幫助'))
async def send_help(bot, ev: CQEvent):
    gid = ev.group_id
    bundle_name = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    services = Service.get_bundles()
    if not bundle_name:
        msg = f'{TOP_MANUAL2}'
        await bot.send_group_msg(group_id=ev['group_id'], message=msg)
        return
    elif bundle_name in bundles:
        msg = gen_bundle_manual(bundle_name, bundles[bundle_name], ev.group_id)
        data_all = []
        data1 ={
            "type": "node",
            "data": {
                "name": '小冰冰',
                "uin": '2854196306',
                "content": msg
            }
            }    
        data_all=[data1]
        await bot.send_group_forward_msg(group_id=ev['group_id'], messages=data_all)
        

@sv.on_prefix(('详细help', '详细帮助', '详细幫助'))
async def send_help(bot, ev: CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    bundle_name = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    if not bundle_name:
        await bot.send(ev, TOP_MANUAL)
        await bot.send(ev, f'当前版本{config.version}')
    elif bundle_name in bundles:
        msg = gen_bundle_manual_all(bundle_name, bundles[bundle_name], ev.group_id)
        data ={
            "type": "node",
            "data": {
                "name": '小冰冰',
                "uin": '2854196306',
                "content": msg
            }
            }
        await bot.send_group_forward_msg(group_id=gid, messages=data)
        
@sv.on_fullmatch(["帮助功能开关"])
async def bangzhu_kg(bot, ev):
    await bot.send(ev, TOP_MANUAL3)