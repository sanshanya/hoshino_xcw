# hoshino_training  

Hoshino调教助手

这是一个满足个人奇怪需求的HoshinoBot插件, 作用是在不破坏星乃??的前提下让星乃的??变成主人的形状.(?????)

说人话: 在不对hoshino文件进行任何修改的情况下, 使用反射特性热替换相关函数, 实现对hoshino某些功能的定制.

本项目地址 https://github.com/zyujs/hoshino_training

## 结构说明

`functions` 目录为模块存放目录, 插件会自动加载该目录下全部.py文件, 您可以根据需要参考预置模块格式自行编写模块并放置在该目录下. `util` 文件夹内文件为针对各种接口的反射工具, 可在模块中使用.

## 预置模块介绍

- `functions/gacha.py` 抽卡功能增强

  移除来一井抽卡后的禁言, 增加"来一井"每日可抽次数至5次.

- `functions/query.py` rank图快捷修改

  将最新rank图以 `rXX-X-服务器.png` 格式放入 `HoshinoBot\res\img\priconne\quick`文件夹中, 不需要重启hoshino, rank系列命令即可输出最新rank图.

- `functions/comic.py` comic模块下载功能增强

  可以为comic模块的检查更新和漫画下载设置超时时间和代理, 避免满屏幕的comic.py报错刷屏, 详见 `functions/comic.py` 内注释.

- `functions/anti-holo.py` anti-holo模块增强

  可以自定义删除容易误伤的触发词, 可以随机发送多个舔狗图.
  请将自行收集的嘲讽vtb舔狗图片放置于 `res/img/anti-holo` 目录, 插件将随机选择图片发送. 如果该文件夹不存在, 插件会尝试发送anti-holo原图片 `res/img/hahaha_vtb_tiangou.jpg`. 如果找不到图片, 插件将发送文字: "vtb舔狗,爬!".

- `functions/chara.py` 角色&卡池自动更新

  本模块将在每次hoshino启动后以及每4个小时自动更新一次角色数据和卡池数据, 无需任何操作. 请注意本模块会和 [pcrbot/gacha](https://github.com/pcrbot/gacha) 卡池自动更新项目冲突, 如果已安装 `gacha` 项目, 请删除本模块(`functions/chara.py`)避免冲突.

  卡池数据来源: <https://api.redive.lolikon.icu/gacha/default_gacha.json>

  角色数据来源: <https://github.com/pcrbot/pcr-nickname> 和 <https://api.redive.lolikon.icu/gacha/unitdata.py>

  本模块部分代码参考了 <https://github.com/pcrbot/gacha> 项目, 感谢作者 [@var-mixer](https://github.com/var-mixer).

- `functions/news.py` 禁用新闻更新

  禁用bili_news_poller,sonet_news_poller服务的检查更新任务, 如果已安装各种新闻或rss插件(如[rss](https://github.com/zyujs/rss)), 可以启动该模块阻止HoshinoBot内置新闻模块检查更新以避免无意义的log刷屏.

  该模块默认禁用, 如需启用, 请将 `news.py.disable` 复制一份并改名为 `news.py`.

## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/zyujs/hoshino_training.git`
1. 在 `config/__bot__.py`的模块列表里加入 `hoshino_training`
1. 重启HoshinoBot

## 许可

本插件以AGPL-v3协议开源
