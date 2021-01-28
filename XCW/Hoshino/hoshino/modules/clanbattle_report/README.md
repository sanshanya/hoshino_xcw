# clanbattle_report

本项目为使用Yobot API数据生成离职报告和会战报告的HoshinoBot插件,由用户自行指定API地址,可使用任意远程服务器的Yobot数据生成报告.

本项目地址 https://github.com/zyujs/clanbattle_report

本项目适用于HoshinoBot v2

## 安装方法:

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/zyujs/clanbattle_report.git`
1. 在 `config/__bot__.py`的模块列表里加入 `clanbattle_report`
1. 重启HoshinoBot

本项目使用的依赖与HoshinoBot相同,一般不需要单独安装依赖,如果出现依赖错误,请自行安装requirements.txt中的依赖.

## 指令列表 :

- `生成会战报告 [@用户] [API地址]` : 生成会战报告
- `生成离职报告 [@用户] [API地址]` : 生成离职报告
- `设置工会api API地址` : (需要管理员权限)为本群设置默认的Yobot工会API
- `查看工会api` : (需要管理员权限)查看本群设置的Yobot API
- `清除工会api` : (需要管理员权限)清除本群设置的Yobot API

例: 
```
生成会战报告 http://localhost:8080/yobot/clan/1234567890/statistics/api/?apikey=abcdefg
生成离职报告 @内鬼 http://localhost:8080/yobot/clan/1234567890/statistics/api/?apikey=abcdefg
设置工会api http://localhost:8080/yobot/clan/1234567890/statistics/api/?apikey=abcdefg
生成会战报告
生成离职报告 @内鬼
```

**API获取方式** : Yobot工会面板 - 统计 - 获取api 

API格式为 `http://{yobot服务器}:{端口}/yobot/clan/{群号}/statistics/api/?apikey={key}`

如果当前群已使用命令设置工会api, 指令可不附带API地址.

加入可选项 `@用户` 表示查看指定用户的报告,需要管理员权限.

每月工会战开始之前生成上次工会战报告,开始后后生成本次工会战报告,国服暂时按照28天周期计算.

## 鸣谢

- 倚栏待月 : 基础代码编写
- 明见 : 背景图片与字体提供
- qq3193377836
- 魔法の書 : 增强显示效果
- 椎名真白 : 本项目基于HoshinoBot交流群椎名真白上传的"retire离职报告yobot版（V2）"项目重构

## 开源

本插件以GPL-v3协议开源
