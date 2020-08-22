import nonebot
from aiocqhttp import Event
from apscheduler.job import Job
from hoshino.service import Service
from nonebot import CommandSession,Message
from aiocqhttp import Event,Message
from hoshino.util4sh import bot, load_config,save_config,add_cron_job,add_delay_job
from collections import defaultdict
from os import path
from typing import List
from hoshino.msghandler import handle_message
from traceback import print_exc
from hoshino.priv import *

bot = nonebot.get_bot()
sv = Service('定时命令',use_priv=ADMIN)
async def task(event):
    if not event:
        return
    uid = event['user_id']
    await bot.send(event,f'下一条消息为成员{uid}设置的定时命令执行结果')
    try:
        await handle_message(bot, event, '_')
    except Exception as ex:
        sv.logger.error(f'执行scheduled command时发生错误{ex}')
    for func in bot._bus._subscribers['message']:
        try:
            await func(event)
        except Exception as ex:
            sv.logger.debug(ex)

_task_path = path.join(path.dirname(__file__),'tasks.json')
_tasks = load_config(_task_path) if load_config(_task_path) else defaultdict(list)
_running_jobs:List[Job] = []

from aiocqhttp import MessageSegment
@sv.on_command('add_cron_job',aliases=('设置周期任务'))
async def _(session:CommandSession):
    hour:str = session.get('hour',prompt='您想几点运行，多个时间用逗号隔开')
    minute:str = session.get('minute',prompt='您想几分运行，多个时间用逗号隔开')
    cmd:str = session.get('cmd',prompt='请输入要运行的指令')
    cmd = cmd.strip('命令') #Hoshino消息只处理一次，加上命令前缀防止触发命令
    session.event.raw_message = cmd
    session.event.message = Message(MessageSegment.text(cmd))
    try:
        global _running_jobs
        job = add_cron_job(task,hour=hour,minute=minute,args=[session.event])
        _running_jobs.append(job)
        global _tasks

        #对event先处理，剔除由RexTrigger添加的match对象
        if 'match' in session.event:
            del session.event['match']

        _tasks['data'].append(dict({
            "id" : job.id,
            "event" : session.event,
            "hour" : hour,
            "minute" : minute
        }))
        save_config(_tasks,_task_path)
        await session.send('设置成功')
    except ValueError as ex:
        sv.logger.error(f'添加定时任务时出现异常{ex}')
        await session.send('参数错误，请重新设置')
    except:
        print_exc()

@sv.on_command('add_delay_job',aliases=('设置延时任务'))
async def _(session:CommandSession):
    delay:str = session.get('delay',prompt='请输入延迟时间,单位为秒')
    if not delay.isdigit():
        await session.send('参数错误，请确保输入为数字')
        session.finish()
    cmd:str = session.get('cmd',prompt='请输入要运行的指令')
    cmd = cmd.strip('命令')
    #将当前event中的消息段替换
    session.event['raw_message'] = cmd
    session.event['message'] = Message([{'type': 'text', 'data': {'text': f'{cmd}'}}])
    try:
        add_delay_job(task=task,delay_time=int(delay),args=[session.event])
        await session.send('设置成功')
    except ValueError as ex:
        await sv.logger.error(f'添加延时任务时出现异常{ex}')
        await session.send('参数错误，请重新设置')

@sv.on_command('show_cron_job',aliases=('查看周期任务'))
async def _(session:CommandSession):
    gid = session.event['group_id']
    reply = ''
    for jb in _running_jobs:
        if jb.args[0].get('group_id') == gid:
            id = jb.id
            cmd = jb.args[0].get('raw_message')
            next_run_time = jb.next_run_time
            reply += f'id:\n{id}\n命令:\n{cmd}\n下次运行时间:\n{next_run_time}\n\n'
    reply = reply.strip()
    if not reply:
        await session.send('周期任务列表为空')
    else:
        await session.send(reply,at_sender=False)
        
@sv.on_command('cancel_cron_job',aliases=('取消周期任务'))
async def _(session:CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run and stripped_arg:
        id = stripped_arg
    else:
        id = session.get('id',prompt='请输入任务id，任务id可通过/show_cron_job得到')
    global _running_jobs
    job_num = len(_running_jobs)
    for jb in _running_jobs[::-1]:
        if jb.id == id:
            _running_jobs.remove(jb)
            global _tasks
            for tsk in _tasks['data'][::-1]:
                if tsk['id'] == id:
                    _tasks['data'].remove(tsk)
    if job_num == len(_running_jobs): 
        await session.send('没有找到该任务')
        session.finish()
    else:
        save_config(_tasks,_task_path)
        await session.send('删除周期任务成功')

#在bot启动时创建计划任务
@bot.on_startup
async def _():
    for tsk in _tasks['data']:
        #构造Event对象event
        event = Event(tsk['event'])
        event.message = Message(tsk['event']['message']) #构造消息段对象
        hour = tsk['hour']
        minute = tsk['minute']
        id = tsk['id']
        try:
            job = add_cron_job(task,id=id,hour=hour,minute=minute,args=[event])
            global _running_jobs
            _running_jobs.append(job)
        except ValueError as ex:
            sv.logger.error(f'添加定时任务时出现异常{ex}')