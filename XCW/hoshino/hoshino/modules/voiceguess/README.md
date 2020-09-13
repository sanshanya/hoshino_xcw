# 猜语音小游戏插件 for HoshinoBot

A [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) based [PCR](http://priconne-redive.jp/) game plugin.


## 简介

基于 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) 开发的小游戏插件，~~需要酷Q Pro~~当前版本基于Mirai开发。

机器人会随机发送一句打开游戏时听到的“cygames”语音，群成员需要在给定时间内猜出语音来自哪位角色。

注意！由于目前go-cqhttp或者cqhttp-mirai对语音的格式有限制，使用前需要自己将插件下载好的m4a语音转为silk格式。转换方法请见“安装方式”一节。


## 功能介绍

|指令|说明|
|-----|-----|
|cygames|机器人随机发送一句“cygames”语音，群友需要猜出这条语音来自哪位角色|
|猜语音排行榜|显示猜语音小游戏猜对次数的群排行榜|


## 安装方式

1. clone或者下载此仓库的代码

2. 将voiceguess文件夹放入`hoshino/modules/`文件夹中

3. 打开`hoshino/config/`文件夹中的`__bot__.py`文件，在`MODULES_ON`中加入一行`'voiceguess',`

4. 运行bot，并在群中发送"cygames"指令。第一次使用时机器人会自动从干炸里脊资源站下载全角色的"cygames"语音，语音是m4a格式，请等待它下完。

5. 前往[silk-v3-decoder](https://github.com/kn007/silk-v3-decoder)项目的[Releases页面](https://github.com/kn007/silk-v3-decoder/releases)下载silk格式转换器。下好后运行，转换模式一定要选“特殊编码 (兼容QQ/微信)”，不然即使转好silk格式go-cqhttp也不认。

6. 将转换好的全部silk格式语音文件放入HoshinoBot的资源文件夹`res/voice_ci`中，并把这个文件夹里之前的m4a语音文件全部删除。

7. 现在可以正常使用猜语音插件了~ 
