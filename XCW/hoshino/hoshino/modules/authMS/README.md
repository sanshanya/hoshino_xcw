# authMS

适用于HoshinoBot v2的授权插件, 可对HoshinoBot的服务层以及对yobot进行授权控制. 大部分功能以天枢授权为蓝本而开发. 本插件另有带有web服务的页面, 如果需要请在此插件的目录下新建vue目录,并下载相关链接中已编译好的文件放入目录下`vue`目录内(可能会有不兼容). 本项目主体框架由[wdvxdr1123](https://github.com/wdvxdr1123)构建, [火龙](https://github.com/xhl6666)添加了一些重要功能. 


本授权系统的开发调试过程均以[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)进行, [cqhttp-mirai](https://github.com/yyuueexxiinngg/cqhttp-mirai)目前也已可以正常上报, 请使用0.2.2.5及以后版本, 西城佬牛逼(大声).


相关链接: 
本项目地址: https://github.com/pcrbot/authMS

HoshinoBot项目地址: https://github.com/Ice-Cirno/HoshinoBot

编译好的vue: https://github.com/wdvxdr1123/pcr-auth-vue

## 特点
* **无GUI** ,不依赖Native环境, 依托于nonebot架构, 对不同的操作系统友好
* 自定义新群试用
* 自定义到期后是否自动退群
* 支持自定义入群发言, 退群发言
* 自定义每日检查频率(最低为每日一次), 可手动快速检查
* 支持无卡密操作, 直接对一个群的授权进行修改/清零
* 支持批量操作(网页/私聊)
* 支持手动提醒群续费(网页)
* 可自动接收好友请求
* 授权检查范围广, 支持以下情形:
  * 被拉近50人以下的群(因为默认不需要被邀请者同意)
  * 超过50人群, 需要机器人同意的群
  * 机器人掉线期间被邀请加入的群
  * 维护者手动登录机器人帐号加入的群
  
  以上情况加入的群聊, 均会收到授权系统的自动检测, 并可自定义退群或开启试用等操作。
  
## 指令示例
**注意, 以下指令中的空格均不可省略**
### 仅限超级管理员私聊的指令
* 【生成卡密 31*5】生成5张31天的卡密
* 【卡密列表】查看已有卡密的信息,后跟数字来查看对应页数
* 【授权列表】查看所有授权群的信息,后跟数字来查看对应页数
* 【管理员帮助】查看管理员指令

### 仅限超级管理员的指令
* 【变更授权 123456789+5】为群123456789增加5天授权, 也可以是减
* 【转移授权 123456*987654】将群123456的剩余时间转移至群987654
* 【授权状态】查询此机器人授权信息的统计, 仅限超级管理员
* 【清除授权 987654】清除群987654的全部授权, 并自动退群(如果配置了的话)
* 【退群 987654】命令退出群聊987654, 但并不清除剩余授权时间
* 【变更所有授权 3】为所有已有授权的群增加3天授权时间
* 【快速检查】立刻检查群的授权, 检查方式与定时任务一样

### 通用指令
* 【检验卡密 abcdefghijklemop】检查卡密的有效性
* 【充值 abcdefghijklemop】群聊使用,为本群充值
* 【充值 abcdefghijklemop*123456789】为群123456789充值
* 【充值帮助】查看充值帮助内容

## 开始使用

1. 在HoshinoBot的modules目录下克隆本项目:
   ```
   git clone https://github.com/pcrbot/authMS.git
   ```
2. 安装依赖, 如下载过慢建议清华镜像: 
   ```
   pip install -r requirements.txt
   ```
3. 以`msghandler.py.example`替换`msghandler.py`文件, 请注意重命名. 
4. 在HoshinoBot统一配置目录下保存配置信息,命名为`authMS.py`, 已提供配置样板`authMS.py.exaplme`, 按照注释修改为您需要的配置


## 其他
* 支持本机多个机器人数据互通, 详情参考`authMS.py.exaplme`中的注释, SQLite是一个本地化的数据库, 因此不支持网络, 配置目录请注意使用斜杠`/`.
  
* 如果您使用Hoshino与yobot的缝合体, `nonebot_plugin.py.example`替换yobot的`nonebot_plugin.py`, 位置:`yobot/yobot/src/client/nonebot_plugin.py`, 注意重命名

* 如果您是初次使用authMS, 且希望配置为到期自动退群, 建议保持默认`ENABLE_AUTH`为0, 待完成全部现有群授权后, 再修改
## 鸣谢
[GitHub@wdvxdr1123](https://github.com/wdvxdr1123)

[GitHub@xhl6699](https://github.com/xhl6666)

## 更新日志

### v0.1.4
更新时间:2020/8/26
* 配置文件新增以下参数：
  * `ENABLE_WEB`, 是否同时启用web管理(之前需在`__init__.py`中配置)
  * `PASSWORD`, web管理密码(之前需在`web_server.py`配置)
  * `REG_HELP_GROUP`, 群聊充值帮助文本
  * `REG_HELP_PRIVATE`, 私聊充值帮助文本
  * `ADMIN_HELP`, 给管理员的帮助文本
  * `FRIEND_APPROVE`, 是否自动接收加好友的请求
* 文件结构调整
* 新增指令【快速检查】【充值帮助】【管理员帮助】
* 新增特性: 处理加好友事件

### v0.1.3
更新时间:2020/8/22 
* 添加`nonebot_plugin.py.example`, 可以实现对yobot的授权控制(虽然早就有了)
* 配置文件新增以下参数:
  * `ENABLE_AUTH`, 授权系统自动检查/退群总开关
  * `FREQUENCY`, 控制授权系统自动检查的频率
  * `GROUPS_IN_PAGE`, 控制每页显示的群的条数
  * `CARDS_IN_PAGE`, 控制每页显示的卡密条数
* 移除配置项目:`ALLOW_PRIVETE_CHECK`
* 优化获取全部授权列表时的参数, 大幅降低API调用次数(尤其是在群较多时)

### v0.1.2
更新时间:2020/8/18

> 本次更新合并了[HoshinoAuthorizeSystem](https://github.com/wdvxdr1123/HoshinoAuthorizeSystem)的功能

* 新增退群，广播功能
* 现在获取已授权群的时时候,会返回群名了
* 使用指令所需权限不足时均增加了提示
* 精简了转移授权部分的代码

### v0.1.1
更新时间:2020/8/18
* 修正Bug#1, 在设置新群使用天数为0时, 自动退群设置不起作用而直接退群
* 新增指令, 为所有已有授权的群修改时间

### v0.1.0
更新时间:2020/8/15
* 初版发布