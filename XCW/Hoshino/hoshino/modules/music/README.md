# Music

<img align="right" src="https://ss0.bdstatic.com/70cFvHSh_Q1YnxGkpoWK1HF6hhy/it/u=1328271432,2672554590&fm=26&gp=0.jpg" alt="logo" width="96px" />

这是一个适用于Hoshino v2的点歌插件,支持搜索并分享多个来源的音乐。

<img src="https://img.shields.io/badge/HoshinoBot-v2.0-brightgreen"/> <img src="https://img.shields.io/badge/cqhttp--mirai-v0.2.3-brightgreen" /> <img src="https://img.shields.io/badge/go--cqhttp-v0.9.24-brightgreen" /> <img src="https://img.shields.io/badge/built_by---LAN---blue"/>


## 说明

音乐分享的支持来自Mirai，请选择合适的插件获得最好的使用体验，如`go-cqhttp`或`cqhttp-mirai`。

如遇使用问题欢迎提交Issue。

*2020/10/18*

- 添加对咪咕音乐的支持。(需要`go-cqhttp` v0.9.29或以上版本)[@wdvxdr1123](https://github.com/wdvxdr1123)

*2020/9/14*

- 请求修改为异步。
- 删除httpx依赖，至此本插件无需任何额外依赖即可运行。

*2020/9/9*

- 添加请求头模板，境外服务器也可以直接使用。[@ishkong](https://github.com/ishkong)

*2020/9/8*

- 更换网易云搜索API，暂不确定请求过于频繁时是否稳定，请不要过度使用。
- 删除对`pycryptodomex`的依赖。
- 非点歌成员使用`[选xx]`关键字仅在距离群内上一次点歌不超过2分钟时才会触发提示，避免日常对话误触。
- 每位成员使用点歌添加3分钟（约一首歌时间)冷却期（避免滥用）。
- 选歌支持一次选择多首，如`[选歌0123]`，刷屏可能导致BOT账号被限制，请按需使用避免刷屏。

*2020/9/7*

- 已支持单独搜索网易和QQ，使用点歌命令时标注歌曲来源。
- 修复了查询失败时的处理机制，使用新版`go-cqhttp`时分享QQ音乐能够显示歌手。

## 安装

下载或克隆本项目，将`music`文件夹放入`modules`文件夹中，并在`config/__bot__.py`的模块列表里加入`music`。

重启HoshinoBot

## 用法

输入以下命令使用：

- \[点歌 好日子\] 点一首歌。
- \[搜网易云 好日子\] 从网易云音乐点一首歌。
- \[搜QQ音乐 好日子\] 从QQ音乐点一首歌。
- \[搜咪咕音乐 好日子\] 从咪咕音乐点一首歌。
- \[选择 0\] 从点歌结果中选择一首。

## 本体

本插件来自[laipz8200的魔改版HoshinoBot](https://github.com/laipz8200/HoshinoBot)。
