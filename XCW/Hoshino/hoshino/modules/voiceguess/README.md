# 猜语音小游戏插件 for HoshinoBot

A [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) based [PCR](http://priconne-redive.jp/) game plugin.


## 简介

基于 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) 开发的小游戏插件，当前版本基于Mirai开发。

机器人会随机发送一句打开游戏时听到的“cygames”语音(支持自定义添加其他语音资源包)，群成员需要在给定时间内猜出语音来自哪位角色。

注意：
1. go-cqhttp的用户请使用v0.9.28或更高的版本，并自行配置ffmpeg。go-cqhttp从这个版本开始已经支持全格式语音发送。

2. 如果你使用的是cqhttp-mirai，那么就不用转换了，直接使用即可，cqhttp-mirai支持发送m4a格式的语音，虽然PC端不能收听。(使用cqhttp-mirai时千万不要再把m4a转成silk了，不然语音会被二压导致音质炸裂)


## 功能介绍

|指令|说明|
|-----|-----|
|cygames|此插件的基础功能，指令自带语音包下载。机器人会随机发送一句“cygames”语音，群友需要猜出这条语音来自哪位角色|
|猜语音|此插件的扩展功能(By @zyujs)。自行添加语音资源包后使用此指令，可发送更多语音供游戏使用(详见下方说明)|
|猜语音排行榜|显示猜语音小游戏猜对次数的群排行榜|

说明：
1. 首次使用`cygames`指令时插件会自动从[干炸里脊资源站](https://redive.estertion.win)上下载cygames语音包，直至语音数量达到代码开头部分设置的`DOWNLOAD_THRESHOLD`。下载的语音被集中存放在`res/voice_ci`文件夹下，其中`res`为HoshinoBot的资源文件夹。由于历史原因(说白了就是偷懒没去重构代码..)，此指令对于自定义添加/删除语音的支持很差，不符合当前需求所趋。如果您仅仅希望便捷、快速地进行游戏，那么使用此指令是您的首选；如果您希望在此基础上高度自定义此插件，请使用下方所介绍的`猜语音`指令。

2. `猜语音`指令（By @zyujs）是基础指令的扩展，通过变更语音文件的存储结构，对于自定义插件更加友好。使用此指令前请自行准备自己所需要的语音资源包，并按角色分别存放于`res/record/[四位数人物ID]`文件夹下。其中，`res`为HoshinoBot的资源文件夹，四位数人物ID可参见HoshinoBot的[角色ID和昵称文件](https://github.com/Ice-Cirno/HoshinoBot/blob/master/hoshino/modules/priconne/_pcr_data.py)。此格式的存储路径兼容其他的一些HoshinoBot插件，如[公主连结人物语音](https://github.com/zyujs/pcr-record)插件或是[xcw再骂我一次](https://github.com/zangxx66/HoshinoBot-xcwRecord)插件。配置好语音资源后，`猜语音`指令会从刚刚配置语音文件中随机选择一个角色，并发送她的一条语音到群里让群友猜。


## 安装方式

1. clone或者下载此仓库的代码

2. 将voiceguess文件夹放入`hoshino/modules/`文件夹中

3. 打开`hoshino/config/`文件夹中的`__bot__.py`文件，在`MODULES_ON`中加入一行`'voiceguess',`

4. 如果你使用的是cqhttp-mirai，那么恭喜，到此为止插件已经可以用了。如果你使用的是go-cqhttp，请使用v0.9.28或更高的版本并自行配置ffmpeg，go-cqhttp从这个版本开始已支持全格式语音发送。

5. 现在可以正常使用猜语音插件了~
