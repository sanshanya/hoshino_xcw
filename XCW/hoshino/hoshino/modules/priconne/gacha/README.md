# gacha
适用于[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的可以自动更新的全限定卡池。包含27个限定卡池, 国服日服台服卡池, 以及混合卡池. 仅测试了v2而没有对v1进行测试. 本卡池默认不会禁言, 抽卡需要@Bot, 如果有需要请自行修改. 

**请务必阅读[开始使用](#开始使用)** 

请注意, 咖啡佬在8月5日提交了一次针对角色名称的修改[b256942](https://github.com/Ice-Cirno/HoshinoBot/commit/7cfa868ec7d6f777ab608b77743af32d34add551#diff-7cb6cbc27352fcca4672d1966d984863),将"游骑兵"更换为了"游侠", 如果您部署的时间早于此时间, 请注意更新角色名称.（[#7](https://github.com/pcrbot/gacha/issues/7)）

想法来自[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)的[#113](https://github.com/Ice-Cirno/HoshinoBot/pull/113), 但是从其源站获取的卡池是数字ID格式, 于是利用`_pcr_data.py`的数据将其转变为第一个中文名称, 更新卡池后原卡池会被备份至`backup.json`, 如出现错误可由此恢复. 

同时可以选择自动更新角色数据和头像, 只会添加本地缺失的角色, 不会影响已有角色, 如果涉及git请注意忽略或提交. 

本项目GitHub地址：https://github.com/pcrbot/gacha

Gitee地址：https://gitee.com/varmixer/gacha

卡池数据更新来源: https://api.redive.lolikon.icu/gacha/default_gacha.json

角色数据更新来源: https://api.redive.lolikon.icu/gacha/unitdata.py

## 指令与功能
* 更新卡池: 更新卡池, 仅限超级管理员, 可群聊可私聊, 无需@, 无需开启服务. 
* 强制更新卡池: 不检查版本而直接覆盖本地卡池
* 选择卡池: 与原指令相同, 请根据提示操作. 
* (自动)自动更新: 每日自动更新卡池. 
  

其余指令与原先抽卡系统一致.


## 开始使用

1. 切换至PCR模块目录下(请自行根据实际情况修改路径):
   ```
   cd ~/HoshinoBot/hoshino/modules/priconne
   ```
2. 移除原有的`gacha/`目录, 建议自行备份以防止出现问题:
   ```
   rm gacha/ -rf 
   ```
3. 在同目录下克隆本项目, 保证目录结构与原来一致, 即`/hoshino/modules/priconne/gacha/`:
   ```
   git clone https://github.com/pcrbot/gacha.git
   ```
4. 移动文件`_pcr_data.py`、`CHARA_NAME.json`、`CHARA_PROFILE.json`到上级目录, 注意需要让`_pcr_data.py`覆盖原来的文件, 此修改与项目的其他插件完全兼容, 仅是修改了数据的保存方式, 因此无需担心（出问题我跑路）
   ```
   cd gacha/
   # 提示覆盖请确认覆盖文件
   mv _pcr_data.py ..
   mv CHARA_NAME.json ..
   mv CHARA_PROFILE.json ..
   ```

## 配置
1. 自动更新出现错误或者是发现新卡池而完成自动更新, 可通知SUPERUSER列表的第一名用户, 如果您想接受到通知, 可以将`update.py`第13行改为`NOTICE = 1`. 

2. `PCRDATA_UPDATA`为`True`时将自动更新角色昵称, 并下载头像. 角色信息保存在外部json文件中, 不会触发热重载. 


## 更新日志

### 2020/11/9
* 将角色信息全部给改为json文件存储, 在启动时读取, 并且加入了动态改变角色昵称的方法， 从而在更新角色数据时不会触发全局热重载
* 兼容最新版[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot), 包含了`CHARA_PROFILE`
* 路径更换为绝对路径, 解决因启动路径而引起的报错
* 自检, **当角色别称出现空字符时, 会自动移除**。
  > 此漏洞会引发什么[问题](https://github.com/pcrbot/HoshinoBot-gacha/commit/7e3cc18f29aaf7d7755d42192e533914fe32a35d)？
  > 当角色别称出现空字符时, 查询竞技场的指令可能导致进入死循环. 
  

### 2020/10/16
* (可选)可以自动更新角色数据(昵称)和自动下载角色头像了 [#9](https://github.com/pcrbot/gacha/issues/9)
* 新增指令【强制更新卡池】可以无视版本号, 强制更新本地卡池(会同时更新角色数据图标)
* 稍微整理了下乱的要命的代码(虽然现在也是)

### 2020/9/29
* 所有请求全部替换为异步调用(使用`hoshino.aiorequests`)
* 定时任务改为`nonebot.scheduler`来触发, 不再依赖hoshino服务层


### 2020/9/10
* 更新了部分游骑兵相关角色名称 [#7](https://github.com/pcrbot/gacha/issues/7)
* 当up角色重复出现在star3中时, 会自动移除 [#8](https://github.com/pcrbot/gacha/issues/8)

### 2020/8/18
* 解决了使用Hoshino后续版本时, 繁体指令提示冲突的问题
* 解决了看看UP时出现USE_CQPRO不存在的问题([#1](https://github.com/pcrbot/gacha/issues/1))

## 本模块原README
本模块基于 0皆无0（NGA uid=60429400）dalao的[PCR姬器人：可可萝·Android](https://bbs.nga.cn/read.php?tid=18434108)，移植至nonebot框架而成。

重构 by IceCoffee

源代码的使用已获原作者授权。
