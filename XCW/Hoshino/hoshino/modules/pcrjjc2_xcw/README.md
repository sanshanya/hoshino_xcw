# pcrjjc2

本插件是[pcrjjc](https://github.com/lulu666lulu/pcrjjc)重置版，不需要使用其他后端api，但是需要自行配置客户端  
[项目地址](https://github.com/qq1176321897/pcrjjc2)

**本项目基于AGPL v3协议开源，由于项目特殊性，禁止基于本项目的任何商业行为**

## 配置方法

1. 更改account.json内的account和password为你的bilibili账号的用户名和密码, admin为管理员的qq，用来接受bilibili验证码进行登录
2. 机器人登录需要验证码时会将链接形式私聊发给admin，这时你需要点进链接正确验证，如果成功，将会出现如下的内容：  
`
validate=c721fe67f0196d7defad7245f6e58d62
seccode=c721fe67f0196d7defad7245f6e58d62|jordan
`  
此时，你需要将验证结果发给机器人，通过指令`/pcrval c721fe67f0196d7defad7245f6e58d62`即可完成验证（~~测试的时候似乎私聊没反应？私聊没反应的话就在群里发也可以，反正不泄露密码，大概率是程序没写好~~已修复 感谢 @assassingyk ）
3. account.json里面的platform和channel分别代表android和b服，emmm最好别改，改了我也不知道可不可以用
4. 如果想推送全部排名变化（而不仅仅是上升排名变化），请切换到分支`notice-all`
