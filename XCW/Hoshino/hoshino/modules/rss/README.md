# rss

适用于Hoshino v2的rss订阅插件

项目地址 https://github.com/zyujs/rss

## 安装方法:

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/zyujs/rss.git`
1. 在 `config/__bot__.py`的模块列表里加入 `rss`
1. 进入本项目根目录,执行 `pip3 install -r requirements.txt` 安装依赖
1. 重启HoshinoBot

默认订阅公主连结b站官方号动态, 请使用指令自行添加/删除关注项.

可以修改插件运行后生成的 `data.json` 文件的 `rsshub` 项自定义rsshub服务器地址.

## 指令列表 :

- `rss help` : 查看帮助
- `rss add rss地址` : 添加rss订阅,需使用完整rss订阅网址.
- `rss addb up主id` 或 `rss add-bilibili up主id` : 添加b站up主订阅
- `rss addr route` 或 `rss add-route route` : 添加rsshub route订阅, route请查询rsshub文档.
- `rss list` : 查看订阅列表
- `rss rm 序号` 或 `rss remove 序号` : 删除订阅列表指定项
- `rss mode 模式id` : 设置推送消息模式 0=标准模式(默认),推送消息包含详情及图片 1=简略模式,推送消息仅包含标题

例: 
```
rss addr /pcr/news  #订阅pcr日服官网新闻
rss addr /pcr/news-cn  #订阅pcr国服官网新闻
rss addr /pcr/news-tw  #订阅pcr台服官网新闻
rss addb 14454663 #订阅席巴鸽b站动态
rss add https://www.zhihu.com/rss #订阅知乎每日精选
rss list  #查看订阅列表
rss remove 0  #删除订阅列表中第1条订阅
rss mode 0  #设置推送消息模式为标准模式
```

## 鸣谢

- @[地河君](https://github.com/Chendihe4975) : 本项目使用 [地河云](https://michikawachin.art/) 的 [RSSHub](https://rsshub.di.he.cn/) 服务作为默认rsshub服务器, 地河喵kkp!

## 许可

本插件以GPL-v3协议开源
