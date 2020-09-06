# hoshino_XCW

一款**自用**的xcwbot,功能丰富,部署十分方便.
如果想要部署教程或插件详情,请移步[wiki](https://github.com/sanshanya/hoshino_xcw/wiki)  
<s>看到那个**自用**没有,另外涩图apikey是上传**公用**的,方便第一次搭bot的人尝试,没人逼你搭这个bot,那些能自己动手获取apikey的就别用本仓库的apikey</s>
***
本仓库原本就是一个收集hoshino插件的仓库,最近有人找我搭bot,为了方便自己**顺便**方便他人搭bot才进行修改的,请不要拿本仓库和其它公主连结bot的installer比较

# 目录

| 文件名  | 描述                          |
| ------- | :---------------------------- |
| hoshino | hoshino本体及其插件集合(主要) |
| miraiGO | miraiGO内为go-cqhttp          |
| miraiOK | miraiOK本体及其插件集合       |
| res     | hoshino所需要的资源文件       |
| 装依赖  | 两个一键装依赖的套餐          |

# 介绍

## hoshino

### 插件表

| 插件名               | 功能描述                                     | 添加方法                                                     | 插件说明                                            |
| :------------------- | -------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------- |
| botmanage            | hoshino原生功能                              | hoshino自带                                                  | 要在原有关键词前加#才能呼出                         |
| dice                 | hoshino原生功能                              | hoshino自带                                                  | 未做任何修改                                        |
| hourcall             | 报时功能,换成了xcw的语音报时                 | 暂时无法使用                                                 | 暂时无法使用                                        |
| kancolle             | 舰娘的远征,hoshino原生功能                   | hoshino自带                                                  | 未做任何修改                                        |
| mikan                | 蜜柑订阅番剧,hoshino原生功能                 | hoshino自带                                                  | 未做任何修改                                        |
| pcrclanbattle        | hoshino自带的会战功能,V3版                   | hoshino自带                                                  | 未做任何修改                                        |
| priconne             | hoshino抽卡及竞技场等的集合                  | 用本插件包的gacha替换hoshino原生gacha                        | 修改为全限定卡池,优化了抽卡的趣味性                 |
| setu                 | 涩图功能,hoshino原生功能                     | hoshino自带                                                  | 未做任何修改                                        |
| translate            | 翻译?,hoshino原生功能                        | hoshino自带                                                  | 未做任何修改                                        |
| twitter              | twitter订阅,hoshino原生功能                  | hoshino自带,但需要相应apikey才能启用                         | 未做任何修改                                        |
| yobot                | 强大的会战管理系统,web和群聊双端管理         | 默认添加方法                                                 | yocool的会战管理界面+特别的帮助页面                 |
| hourcallyao          | 买药提醒功能                                 | 默认添加方法                                                 | 内含东9区和东8区两个时区的提醒,在"*lssv*"中自行开关 |
| **shebot_old**       | 强大的涩图插件                               | 默认添加方法,且注意shebot自带*service.py*需放在*run.py*同目录,且需要apikey才能启用在线搜图. | 涩图撤回+r18开关+私聊发图......小心bot被盯上        |
| reload               | hoshino的重启插件                            | 默认添加方法,且注意修改*run.py*,将`use_reloader=True`改为`use_reloader=False` | 目前对cqhttpmirai的适配不是很好                     |
| longwang             | 迫害龙王功能                                 | 暂时无法使用                                                 | 暂时无法使用                                        |
| **tarot**            | 塔罗牌功能                                   | 默认添加方法                                                 | 来一局塔罗牌吧,注意规则                             |
| flac                 | 搜无损音乐,,hoshino原生功能                  | hoshino自带                                                  | 未做任何修改                                        |
| shitu                | 识图功能                                     | 默认添加方法,需要apikey才能正常使用                          | 可进行一些自定义的修改,具体参照源码                 |
| shifan               | 搜番功能                                     | 默认添加方法                                                 | 可进行一些自定义的修改,具体参照源码                 |
| **ClanBattleReport** | 会战报告生成                                 | 默认添加方法,需要修改ip                                      | 生成离职和会战报告,未来会有更多样式                 |
| **vortune**          | 生成运势小卡片                               | 默认添加方法                                                 | 你喜欢的vtuber给你的小卡片                          |
| **acggov**           | 涩图功能+日排行                              | 默认添加方法,且在*config*内添加*acggov.py*,需要apikey才能启用 | 太pro,纯度太高                                      |
| bot_manager_web      | 网页端的"*lssv*"                             | 默认添加方法,且在*config*内添加*bot_manager_web.py*,且按说明进行配置 | 非常实用的功能                                      |
| voiceguess           | 通过语音猜角色                               | 暂时不可用                                                   | 暂时不可用                                          |
| eclanrank            | 定时提醒工会的排名                           | 默认添加方法                                                 | 定时播报,显示档线和名次变化幅度,emm....班主任的感觉 |
| tencent_ai_reply     | 腾讯AI闲聊                                   | 默认添加方法,需要相应apikey                                  | 有点鸡肋                                            |
| QA                   | 问答(调教)功能                               | 默认添加方法                                                 | 有更好的选择                                        |
| hiumsentences        | 网易云语录                                   | 默认添加方法                                                 | 到点,上号!                                          |
| generator            | 狗屁不通生成器,营销文生成器等四个功能        | 默认添加方法                                                 | 有趣但无聊?                                         |
| ontree_scheduler     | 挂树优化提醒                                 | 默认添加方法,且需要安装其说明修改yobot                       | 挺好的功能                                          |
| **image**            | 自定义生成表情包                             | 默认添加方法,另外需要*image_data*,需要修改本模块的*mian.py*  | 栞栞:"给我栞栞"                                     |
| eqa                  | 一款优秀的问答(调教)功能                     | 默认添加方法                                                 | 我问A你答B                                          |
| russian              | 俄罗斯轮盘赌                                 | 默认添加方法                                                 | 开枪!                                               |
| explosion            | 每天一发惠惠                                 | 暂时无法使用                                                 | 暂时无法使用                                        |
| boxcolle             | BOX查询功能                                  | 默认添加方法                                                 | 有点不好用                                          |
| timeline             | 轴上传                                       | 默认添加方法                                                 | 你就是泄轴的内鬼?                                   |
| **picapi**           | 自定义拉取图片                               | 默认添加方法                                                 | apikey和图床地址,moduomoduo....                     |
| aircon               | 群空调                                       | 默认添加方法                                                 | 天气这么热,开点精神上的空调                         |
| authMS               | 群授权功能                                   | 默认添加方法,暂时有一定问题                                  | 开启后自行寻找解决办法                              |
| schedule             | 国服日程表                                   | 默认添加方法                                                 | ...........                                         |
| bilisearchspider     | b站订阅                                      | 默认添加方法                                                 | ...........                                         |
| pcravatarguess       | 图片猜角色                                   | 默认添加方法                                                 | 考验你厨力的时候到了                                |
| pcrdescguess         | 通过角色描述猜角色                           | 默认添加方法                                                 | 你了解自己的老婆嘛?                                 |
| shebot_new           | 集合了许多插件,请勿和shebot及QA及eqa同时开启 | *hoshino*内添加*util4sh.py*并配置,shebot_new内的各个插件也需要分别按说明配置 | 待月tql                                             |
| nmsl                 | 抽象话抽象抽象                               | 默认添加方法                                                 | 把正常话转化为抽象话                                |
| baidupan             | 百度网盘或秒传链接解析                       | 默认添加方法                                                 | ...........                                         |
| calendar             | 又一个查看日程的插件                         | 默认添加方法                                                 | 优点是全服务器可用                                  |
| clanbattle_report    | 可通过api生成会战报告                        | 默认添加方法                                                 | 海星..........                                      |
| meme_web             | 合并原homework和memegenerator                | 默认添加方法                                                 | web端和群聊上传和删除表情以及搜索表情               |

**加粗部分的插件需要修改路径才能正常使用**

......

## miraiOK

待补充....

## miraiGO

简单易用,强烈推荐



## res

hoshino需要的res文件

## 装依赖

两个方便装依赖的套餐

