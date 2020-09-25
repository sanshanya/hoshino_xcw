# clanbattle_rank

本项目为查询公会战排名信息的HoshinoBot插件,使用 [wiki.biligame.com](https://wiki.biligame.com/pcr/%E5%9B%A2%E9%98%9F%E6%88%98%E5%88%86%E6%95%B0%E6%9F%A5%E8%AF%A2%E5%B7%A5%E5%85%B7) API获取数据.

本项目地址 https://github.com/zyujs/clanbattle_rank

本项目适用于HoshinoBot v2

**注意**: 公会战结束当天24点后到公会战结果发布前,该API无法使用,表现为任何查询都会返回"数据获取失败".B站可能会改动API接口导致插件无法使用,如遇异常请等待本项目更新.

## 安装方法:

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/zyujs/clanbattle_rank.git`
1. 在 `config/__bot__.py`的模块列表里加入 `clanbattle_rank`
1. 重启HoshinoBot

## 模块说明 :

本插件含有两个模块: 
- `clanbattle_rank` : 插件的基础功能
- `clanbattle_rank_push` : 每日公会战排名信息推送

其中推送功能仅在公会战期间推送信息, 分别为前6天的5:30和第6天的23:55, 如果不需要推送, 请自行关闭 `clanbattle_rank_push` 模块.

## 指令列表 :

- `查询排名 公会名 [会长名]` : 查询指定公会排名
- `查询分段` : 查询分段信息
- `查询关注` : 查询关注的公会信息
- `添加关注 公会名 [会长名]` : (需要管理员权限)将指定公会加入关注列表,如有重名需要附加会长名
- `删除关注 公会名` : (需要管理员权限)将指定公会从关注列表中删除
- `清空关注` : (需要管理员权限)清空关注列表

如果要查询或添加关注的公会名或会长名带有空格, 请使用 `[]` 把名字包起来, 例如 ` 添加关注 [公会名] [会长名] `, 注意公会名和会长名都要加.

例: 
```
查询排名 美少女战士
查询排名 美少女战士 布丁可可
添加关注 美少女战士 布丁可可
添加关注 [内鬼连接] [佑树 挖矿中 刺必还]
查询关注
```

## 开源

本插件以GPL-v3协议开源
