import nonebot
import hoshino
from functools import wraps

def seheduler_func(func):
    @wraps(func)
    async def wrapper():
        try:
            hoshino.logger.info(f'[hoshino_training] Scheduled job {func.__name__} start.')
            ret = await func()
            hoshino.logger.info(f'[hoshino_training] Scheduled job {func.__name__} completed.')
            return ret
        except Exception as e:
            hoshino.logger.error(f'[hoshino_training] {type(e)} occured when doing scheduled job {func.__name__}.')
            hoshino.logger.exception(e)
    return wrapper

def scheduler_replace(func_ref, func):
    jobs = nonebot.scheduler.get_jobs()
    for job in jobs:
        if job.func_ref == func_ref:
            job.func = func
            return True
    return False

def scheduler_remove(func_ref):
    jobs = nonebot.scheduler.get_jobs()
    for job in jobs:
        if job.func_ref == func_ref:
            job.remove()
            return True
    return False

def scheduler_get_ref_list():
    ref_list = []
    jobs = nonebot.scheduler.get_jobs()
    for job in jobs:
        ref_list.append(job.func_ref)
    return ref_list
