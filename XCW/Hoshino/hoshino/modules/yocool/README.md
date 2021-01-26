![](https://i.loli.net/2020/11/15/YCBtcIVK4P6Hdfx.png)
# YoCool-Console——YoCool控制台
<p align="left">
<a href='https://github.com/Ice-Cirno/HoshinoBot'><img src="https://img.shields.io/badge/HoshinoBot-v2.0-green.svg"/></a>
<a href='https://github.com/pcrbot/yobot'><img src="https://img.shields.io/badge/yobot-v3.0-brightgreen.svg"/></a></a>
<a href='https://github.com/pcrbot/YoCool-Console/blob/master/LICENSE'><img src="https://img.shields.io/github/license/A-kirami/YoCool-Console"/></a>
</p>

本项目为实现[YoCool](https://github.com/A-kirami/YoCool)的一键安装、切换主题、升级、卸载等便捷管理操作的[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)V2插件

[YoCool](https://github.com/A-kirami/YoCool)是[yobot](https://github.com/pcrbot/yobot)的会战管理后台美化项目，拥有多种主题风格可供选择，提供对PC端和移动端更好的布局适配，以及对用户更友好的交互逻辑，让你的[yobot](https://github.com/pcrbot/yobot)界面更加多彩

注意：使用本插件前你还需要安装插件版或源码版[yobot](https://github.com/pcrbot/yobot)

## 目录
- [开始使用](https://github.com/pcrbot/YoCool-Console/#开始使用)
    - [使用Gitclone安装](https://github.com/pcrbot/YoCool-Console/#使用Gitclone安装)
    - [使用Hoshino-cli安装](https://github.com/pcrbot/YoCool-Console/#使用Hoshino-cli安装)
- [操作指令](https://github.com/pcrbot/YoCool-Console/#操作指令)
- [注意事项](https://github.com/pcrbot/YoCool-Console/#注意事项)


## 开始使用

### 使用Gitclone安装

1. 进入hoshino的``modules``文件夹<br>

2. 输入以下命令克隆本仓库
    ```
    git clone https://github.com/pcrbot/YoCool-Console.git
    ```
3. 修改``_bot_.py``，在``MODULES_ON``中添加``YoCool-Console``

4. 【插件版跳过本步骤】复制``yocool.py.example``到``config``文件夹，重命名为``yocool.py``，打开后按照注释进行配置

5. 重启HoshinoBot


### 使用[Hoshino-cli](https://github.com/pcrbot/hsn)安装

1. 输入以下命令安装YoCool-Console
    ```
    hsn install yocool
    ```
2. 【插件版跳过本步骤】复制``yocool.py.example``到``config``文件夹，重命名为``yocool.py``，打开后按照注释进行配置

3. 重启HoshinoBot


## 操作指令
以下指令请私聊Bot进行操作（目前仅支持主题PrincessAdventure，CoolLite尚在开发中）
|指令|说明|
|-----|-----|
|一键安装|使用默认主题快速安装YoCool，也可使用``一键安装 主题名``来指定安装哪个主题|
|切换主题|切换YoCool的主题，使用``切换主题 主题名``来选择切换到哪个主题|
|更新YoCool|更新YoCool到最新版本，指令前带``强制``可以强制执行本条指令|
|卸载YoCool|将YoCool从yobot中卸载，指令前带``强制``可以强制执行本条指令|


## 注意事项

1. 本插件直接使用了相对路径读写，请保证运行机器人主程序时，当前目录为`run.py`同级目录，例如：
   ```
   # 使用如下命令行运行时可正常
   python3 run.py

   # 不可, 当前目录不符合要求
   python3 /root/HoshinoBot/run.py
   ```

2. 安装与卸载时，由于移动文件和解压缩，会短时间内堵塞，约5~10秒，具体时间取决于您服务器的IO性能。

3. 使用了[fastgit](http://fastgit.org/)源来进行github的加速下载。您也可以自行修改第34行。
