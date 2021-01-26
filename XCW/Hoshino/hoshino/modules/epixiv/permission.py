import time
from . import util

# 初始化配置文件
config = util.get_config()
# 初始化数据库
db = util.init_db(config.cache_dir, 'permission')


class user:
    uid: int
    timeout: int
    info: {}

    def __init__(self, uid, timeout=0):
        self.uid = uid
        self.timeout = timeout
        info = db.get(uid, {})
        info.setdefault('create_time', time.time())
        info.setdefault('running', False)
        info.setdefault('msg', '处理中')
        self.info = util.Dict(info)

    def running(self, msg='处理中'):
        self.info.create_time = time.time()
        self.info.msg = msg
        self.info.running = True
        self.__save_info()

    def done(self, msg='成功'):
        self.info.msg = msg
        self.info.running = False
        self.__save_info()

    def check(self):
        # time.strftime('%d', time.localtime())
        if self.info.create_time + self.timeout < time.time() and not self.timeout == 0:
            self.done()
            return False
        return self.info.running

    def msg(self):
        return self.info.msg

    def __save_info(self):
        db[self.uid] = self.info
