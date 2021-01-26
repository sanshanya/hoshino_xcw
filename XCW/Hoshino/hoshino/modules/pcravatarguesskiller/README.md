# pcravatarguesskiller
猜头像杀手（疯狂电脑）

*用于一个群有两个机器人且另一个机器人开启了猜头像（图片）功能的情况。

通过hoshino\modules\priconne\_pcr_data.py中的CHARA_NAME字典读取角色id列表，通过这个列表去角色头像文件夹中获取头像图片进行雪碧图拼接，然后利用OpenCV进行图像匹配。

指令：
  
  生成json
  
    记录所有角色头像文件的arraylist并存到json文件中
    
  更新json
  
    更新已经生成的json文件
  
  生成sprite图
  
    拼接一张包含所有角色的一星三星六星头像的雪碧图
  
  更新sprite图（先更新json）
  
    更新已经生成的雪碧图


开启avatarguess_killer的机器人会参与猜头像的竞猜，难度为疯狂电脑，努力击败bot吧！
