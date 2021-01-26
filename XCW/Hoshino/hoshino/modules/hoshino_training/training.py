import nonebot
import os
import importlib
import traceback

def get_functions_list():
    fnlist = []
    path = os.path.join(os.path.dirname(__file__), 'functions')
    if not os.path.exists(path):
        return fnlist
    for fn in os.listdir(path):
        s = fn.split('.')
        if len(s) >=2 and s[-1] == 'py':
            fnlist.append(s[0])
    return fnlist

def load_functions(flist):
    for name in flist:
        try:
            importlib.import_module('hoshino.modules.hoshino_training.functions.' + name)
            print('[hoshino_training] load module', name, 'successed')
        except:
            print('[hoshino_training] load module', name, 'failed')
            traceback.print_exc()

@nonebot.on_startup
async def startup():
    flist = get_functions_list()
    load_functions(flist)
