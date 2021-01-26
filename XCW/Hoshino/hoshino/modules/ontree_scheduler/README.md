# 挂树提醒插件 <font size=3>V1.0</font> *for* HoshinoBot V1<br><font size=3>*Plugin [ Ontree Scheduler Ver1.0 ] for HoshinoBot V1* - *by Rayee*</font>  

> ## 功能介绍  
> 因 公主连结 游戏机制导致挂树时间限制1小时  
> 本插件通过粗略时间计算提醒玩家及时下树 避免掉刀  
> PS：插件轮巡机制支持多群同时使用  

<br>  

>## 使用说明  
>使用本插件需要更改以下内容
>>Hoshino/config.py 添加插件 ontree_scheduler  
>>yobot 公会战设置中取消 挂树/取消挂树 两个命令在群中的提示  
>>修改 ontree_scheduler.py 第8,34行来更换 挂树/取消挂树 的命令  
>>修改 ontree_scheduler.py 第56行来改变轮巡器的时间周期（默认3分钟检查一次）
>>  
>>PS1：请勿删除 tree.db , 该文件记录玩家上树时间及信息  
>>PS2：挂树数据若未接收 取消挂树 指令将会在一小时期限后自动删除  
  
<br>  

>## 使用方法  
>发送 挂树* 指令进行记录   
>若 挂树期限结束前下树 发送 取消挂树* 指令删除记录  
>若 挂树期限结束10分钟内仍未下树 BOT会三次*提醒下树 时间超过期限后记录自动删除  
>  
>PS*：两条指令可自定义，BOT的提醒次数会因为轮巡器时间周期而改变
  
<br>  

### 本插件为作者测试后的1.0版本，不确定功能稳定，若发现BUG请反馈作者  
### *Rayee Programed on 2020/08/04*