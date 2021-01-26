import re

class rss():
    # 定义基本属性
    url = ''  # 订阅地址
    group_id = []  # 订阅群组

    # 返回订阅链接
    def geturl(self) -> str:
        rsshub = 'https://rsshub.app/twitter/user/'
        return rsshub + self.url + '/exclude_rts_replies=true'
