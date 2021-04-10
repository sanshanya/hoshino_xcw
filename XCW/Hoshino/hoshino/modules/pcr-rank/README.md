# pcr-rank
A auto-update rank list module for hoshino   
一个自动更新rank表的插件，更新源[ColdThunder11/pcr-rank_data](https://github.com/ColdThunder11/pcr-rank_data)
## 使用方法
将本项目clone至HoshinoBot\hoshino\modules下，在__bot__.py中加入pcr-rank   
！！注意！！本插件与自带rank表指令冲突，在启用前请先修改HoshinoPath\hoshino\modules\priconne\query内的query.py和__init__.py删除有关指令及其帮助   
## 指令列表
| 指令 | 备注 |
| ------ | ------- |
| 查询指令同原机器人自带 | 无 |
| 查看当前rank更新源 | 字面意思 |
| 查看全部rank更新源 | 列出远程rank表更新源 |
| 设置rank更新源 国/台/日 稳定/自动更新 源名称 | 无 |
| 更新rank表缓存 | 手动更新rank表缓存 |
## 说明
有问题/其他rank表更新源/rank表更新了可以在Issues里提或者在星乃和优妮群里找我。就酱。
## Update 2020.3.4
！！注意2.0！！本次更新与老版本配置文件不兼容，建议扬了重新弄或者自己改，如果没扬清重新更新一次缓存   
现在图片会启用分块下载并在本地缓存，解决gocq下载超时的问题   
现在可以设置自己的镜像源
## TODO
自动压缩过大的图片（下次一定

