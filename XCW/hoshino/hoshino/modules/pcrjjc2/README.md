# pcrjjc2

本插件是[pcrjjc](https://github.com/lulu666lulu/pcrjjc)重置版，不需要使用其他后端api，但是需要自行配置客户端

**本项目基于AGPL v3协议开源，由于项目特殊性，禁止基于本项目的任何商业行为**

## 配置方法

1. 环境需求：.net framework 4.5及以上 jre8
2. 用模拟器或**root过**的手机打开公主连结，并且游客登录或者账号登录，**并过完全部教程**
3. 复制模拟器/data/data/com.bilibili.priconne/shared_prefs文件夹下的bili_key.xml和TouristLogin.xml或login.xml(如果是游客登录就是touristlogin.xml, 如果是账号登录是login.xml)，放置到项目目录toolchain文件夹下
4. 运行BiliPrefReader.exe
5. 复制生成的touristlogin.json或者login.json到项目根目录(pcrjjc2文件夹)下，并重命名为account.json
6. 本插件仅依赖于account.json即可以运行，不需要同时开着模拟器也不需要toolchain下任何其他文件，~~更不需要在服务器上开模拟器~~
