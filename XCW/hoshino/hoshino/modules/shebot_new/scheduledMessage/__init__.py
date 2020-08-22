import os
import time
from aiocqhttp.event import Event
import nonebot
from nonebot.command import CommandSession
from hoshino.service import Service
from hoshino.util4sh import add_cron_job, load_config,save_config,broadcast
from hoshino.priv import *

job_path = os.path.join(os.path.dirname(__file__),'jobs.json')
sv = Service('闹钟', use_priv = OWNER)
bot = nonebot.get_bot()


async def send_group_msg(gid,msg):
    await bot.send_group_msg(group_id=gid,message=msg)

saved_jobs = load_config(job_path)
running_jobs = [] #正在运行的任务

@sv.on_command('hourclock', aliases=('闹钟','设置计划任务'))
async def add_job(session: CommandSession):
    global saved_jobs
    global running_jobs
    stripped_arg = session.current_arg_text.strip()
    id = str(time.time())
    if session.is_first_run and stripped_arg:
        id = stripped_arg
    gid = session.event['group_id']
    hour: str = session.get('hour',prompt='您想几点运行，多个时间用逗号隔开')
    minute: str = session.get('minute',prompt='您想几分运行，多个时间用逗号隔开')
    msg: str = session.get('msg', prompt='请输入要发送的内容')
    saved_jobs[id] = {
        'groups' : [gid],
        'hour' : hour,
        'minute' : minute,
        'msg' : msg
    }
    try:
        job = add_cron_job(send_group_msg,id=id,hour=hour,minute=minute,args=[gid,msg])
        running_jobs.append(job)
        save_config(saved_jobs,job_path)
        await bot.send(session.event,f'好的,我记住了,将在每天{hour}点{minute}分发送{msg}',at_sender=True)
    except Exception as ex:
        sv.logger.error(f'添加定时任务时出现异常{ex}')
        await session.finish('参数错误，请重新设置')

@sv.on_keyword('查看计划任务')
async def _(bot,event):
    if not running_jobs:
        await bot.send(event,'没有正在运行的计划任务',at_sender=False)
        return
    reply = ''
    for job in running_jobs:
        try:
            reply += f'id:\n{job.id}\n下次运行时间:\n{job.next_run_time.strftime("%Y-%m-%d-%H:%M:%S")}\n发送内容:\n{job.args[0]}\n\n'
        except:
            running_jobs.remove(job)
    await bot.send(event,reply.strip(),at_sender=False)

@sv.on_prefix('删除计划任务')
async def delete_job(bot, event: Event):
    global running_jobs
    global saved_jobs
    id = event.raw_message.strip('删除计划任务')
    if id in saved_jobs:
        del saved_jobs[id]
        save_config(saved_jobs,job_path)
    for job in running_jobs:
        if id == job.id:
            running_jobs.remove(job)
            job.remove()
            await bot.send(event,'已删除计划任务')

@bot.on_startup
async def load_saved_jobs():
    #将json文件中的计划任务启动
    global running_jobs
    for k in saved_jobs:
        groups = saved_jobs[k]['groups']
        hour = saved_jobs[k]['hour']
        minute = saved_jobs[k]['minute']
        msg = saved_jobs[k]['msg']
        job = add_cron_job(broadcast,id=k,hour=hour,minute=minute,args=[msg,set(groups),sv.name]) if groups!='default' else \
            add_cron_job(broadcast,id=k,hour=hour,minute=minute,args=[msg,None,sv.name])
        running_jobs.append(job)
        print(f'job {job.id} added')


"""     robj = re.match(r'(\d{1,2})点(\d{1,2})发送(.{1,100})',message)
    if robj:
        hr = int(robj.group(1))
        min = int(robj.group(2))
        msg = robj.group(3)
        now = datetime.datetime.now()
        run_date = datetime.datetime(now.year,now.month,now.day,hr,min)
        try:
            job = add_date_job(send_group_msg,id=now_str,run_date=run_date,args=[gid,msg])
            running_jobs.append(job)
            await bot.send(event,'好的，我记住了',at_sender=True)
        except:
            await bot.send(event,'添加任务失败,请检查参数')
            return

    robj = re.match(r'(\d{1,2})?小?时?(\d{1,2})分钟后发送(.{1,100})',message)
    if robj:
        try:
            delta_hr = int(robj.group(1))
        except:
            delta_hr = 0
        try:
            delta_min = int(robj.group(2))
        except:
            delta_min = 0
        msg = robj.group(3)
        now = datetime.datetime.now()
        run_date = now + datetime.timedelta(hours=delta_hr,minutes=delta_min)
        try:
            job = add_date_job(send_group_msg,id=now_str,run_date=run_date,args=[gid,msg])
            running_jobs.append(job)
            await bot.send(event,f'好的，我记住了',at_sender=True)
        except:
            await bot.send(event,'添加任务失败,请检查参数')
            return """