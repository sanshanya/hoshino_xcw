import nonebot
import hoshino

def _get_module(module):
    plugins = nonebot.get_loaded_plugins()
    for plugin in plugins:
        m = str(plugin.module)
        m = m.replace('\\', '/').replace('//', '/')
        if module in m:
            return plugin.module
    return None

def module_replace(module_path, member_name, func):
    module = _get_module(module_path)
    if not module:
        return False
    if not hasattr(module, member_name):
        return False
    setattr(module, member_name, func)
    return True

def module_get(module_path, member_name):
    module = _get_module(module_path)
    if not module:
        return None
    if not hasattr(module, member_name):
        return None
    return getattr(module, member_name)
