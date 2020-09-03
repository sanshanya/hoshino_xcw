from datetime import timedelta
from . import *
from datetime import *
key_dict = msghandler.key_dict
group_dict = msghandler.group_dict
trial_list = msghandler.trial_list

try:
    config = hoshino.config.authMS.auth_config
except:
    # 保不准哪个憨憨又不读README呢
    hoshino.logger.error('authMS无配置文件!请仔细阅读README')

def generate_key():
    '''
    生成16位卡密
    '''
    new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    while new_key in key_dict:  # 防止生成重复的卡密, 不过概率太低了。。。
        new_key = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return new_key

def add_key(duration):
    '''
    卡密添加到数据库中
    '''
    new_key = generate_key()
    key_dict[new_key] = duration
    return new_key

def get_key_list():
    '''
    获取全部的卡密列表
    '''
    key_list = []
    for key, value in key_dict.iteritems():
        key_list.append({'key': key, 'duration': value})
    return key_list

def del_key(key):
    '''
    删除一张卡密, 成功返回True
    '''
    if key in key_dict:
        key_dict.pop(key)
        return True
    return False

def update_key(key, duration):
    '''
    更新一张卡密,成功返回True
    '''
    if duration <= 0:
        # 禁止将有效期更新为0, 因为检验卡密时以0为无效标志
        return False
    if key in key_dict:
        key_dict[key] = duration
        return True
    return False

def query_key(key):
    '''
    检查一张卡密, 有效则返回可以增加的授权时间, 无效则返回0
    '''
    if key in key_dict:
        return key_dict[key]
    else:
        return 0


def check_group(gid):
    '''
    检查一个群是否有授权, 如果有返回过期时间（datetime格式）, 否则返回False. 
    注意无论Bot是否加入此群都会返回
    '''
    if gid in group_dict:
        return group_dict[gid]
    else:
        return 0

def reg_group(gid, key):
    '''
    为一个群充值, 卡密无效则返回False, 否则返回剩余有效期（datatime格式）
    '''
    days = query_key(key)
    if days == 0:
        return False
    past_time = change_authed_time(gid, days)
    del_key(key)
    return past_time

def change_authed_time(gid, time_change=0, operate=''):
    '''
    不使用卡密, 而直接对一个群的授权时间进行操作
    '''
    if operate == 'clear':
        try:
            # 用try是因为可能会尝试给本来就无授权的群清空授权, 此种情况并不需要另外通知, 因为最终目的一致
            group_dict.pop(gid)
        except:
            pass
        return 0

    if gid in group_dict:
        group_dict[gid] = group_dict[gid] + timedelta(days=time_change)
    else:
        today = datetime.now()
        group_dict[gid] = today + timedelta(days=time_change)
    return group_dict[gid]

async def get_group_name(group_id=0):
    '''
    1. 传入一个整型数字, 返回群名字符串
    2. 传入一个list, 内含多个群ID, 返回一个字典, 键为群ID(int),值为群名 
    3. 不填入参数, 返回一个包含所有群ID与群名对应关系的字典
    '''

    group_list_all = await get_group_list_all()
    _gids=[]
    _gnames=[]
    # 获得的已加入群为列表形式, 处理为需要的字典形式
    for it in group_list_all:
        _gids.append(it['group_id'])
        _gnames.append(it['group_name'])
    group_name_dir_all = dict(zip(_gids,_gnames))

    if group_id == 0:
        return group_name_dir_all
    if type(group_id) == list:
        group_name_dir = {}
        for gid in group_id:
            group_name_dir[int(gid)] = group_name_dir_all.get(int(gid))
        return group_name_dir
    
    
    return group_name_dir

async def get_authed_group_list():
    '''
    获取已授权的群
    '''
    authed_group_list = []
    group_name_dir = await get_group_name()


    for key, value in group_dict.iteritems():
        deadline = f'{value.year}年{value.month}月{value.day}日 {value.hour}时{value.minute}分'
        group_name = group_name_dir.get(int(key),'未知')
        authed_group_list.append({'gid': key, 'deadline': deadline, 'groupName': group_name})
    return authed_group_list

async def get_group_list_all():
    '''
    获取所有群, 无论授权与否, 返回为原始类型(列表)
    '''
    bot = nonebot.get_bot()
    self_ids = bot._wsr_api_clients.keys()
    for sid in self_ids:
        group_list = await bot.get_group_list(self_id=sid)
    return group_list


async def process_group_msg(gid, expiration, title:str='',end='',group_name_sp=''):
    '''
    把查询消息处理为固定的格式 \n
    第一行为额外提醒信息（例如充值成功）\n
    群号：<群号> \n
    群名：<群名> \n
    授权到期：<到期时间> \n
    部分情况下, 可以通过指定群组名的方式来减少对API的调用次数（我并不知道这个对性能是否有大影响）
    '''
    if group_name_sp == '':
        bot = nonebot.get_bot()
        self_ids = bot._wsr_api_clients.keys()
        for sid in self_ids:
            try:
                group_info = await bot.get_group_info(self_id=sid, group_id=gid)
                group_name = group_info['group_name']
            except:
                group_name = '未知(Bot未加入此群)'
    else:
        group_name = group_name_sp
    time_format = expiration.strftime("%Y-%m-%d %H:%S:%M")
    msg = title
    msg += f'群号：{gid}\n群名：{group_name}\n到期时间：{time_format}'
    msg += end
    return msg

def new_group_check(gid):
    '''
    加入新群时检查此群是否符合条件,如果有试用期则会自动添加试用期授权时间, 同时添加试用标志
    '''
    if gid in group_dict:
        time_left = group_dict[gid] - datetime.now()

        if time_left.total_seconds() <= 0:
            # 群在列表但是授权过期, 从授权列表移除此群
            group_dict.pop(gid)
            return 'expired'

        return 'authed'

    if config.NEW_GROUP_DAYS <= 0 or gid in trial_list:
        return 'no trial'
    # 添加试用标记
    trial_list[gid] = 1
    # 添加试用天数
    change_authed_time(gid=gid,time_change=config.NEW_GROUP_DAYS)
    return 'trial'

def transfer_group(old_gid, new_gid):
    '''
    转移授权,新群如果已经有时长了则在现有时长上增加
    '''
    today = datetime.now()
    left_time = group_dict[old_gid] - today if old_gid in group_dict else timedelta(days=0)
    group_dict[new_gid] = left_time + (group_dict[new_gid] if new_gid in group_dict else today)
    group_dict.pop(old_gid)

async def gun_group(gid):
    '''
    退出群聊
    '''
    try:
        await nonebot.get_bot().set_group_leave(group_id=gid)
    except CQHttpError:
        return False
    return True


async def notify_group(gid, txt):
    '''
    发送自定义提醒广播,顺带解决了HoshinoBot和Yobot的广播短板
    '''
    try:
        await nonebot.get_bot().send_group_msg(group_id=gid, message=txt)
    except CQHttpError:
        return False
    return True