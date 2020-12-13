import os
import time
import random
from  datetime import datetime
from hoshino import util
from hoshino import Service
from .data_source import add_text,pic_to_b64

sv = Service('报时', visible= False, enable_on_default= True, bundle='报时', help_='''
生成一张报时图
'''.strip())
@sv.on_fullmatch('报时')
async def showtime(bot, event):
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    hour_str = f' {hour}' if hour<10 else str(hour)
    minute_str = f' {minute}' if minute<10 else str(minute)
    num = random.randint(1, 7)
    if num == 1:
        template_path = os.path.join(os.path.dirname(__file__),'template1.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=39,textfill='black',position=(135,115))
    elif num == 2:
        template_path = os.path.join(os.path.dirname(__file__),'template2.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=39,textfill='black',position=(135,115))
    elif num ==3:
        template_path = os.path.join(os.path.dirname(__file__),'template3.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=90,textfill='black',position=(302,278))
    elif num ==4:
        template_path = os.path.join(os.path.dirname(__file__),'template4.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=73,textfill='black',position=(200,295))
    elif num ==5:
        template_path = os.path.join(os.path.dirname(__file__),'template5.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=105,textfill='black',position=(244,375)) 
    elif num ==6:
        template_path = os.path.join(os.path.dirname(__file__),'template6.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=100,textfill='black',position=(246,373))
    elif num ==7:
        template_path = os.path.join(os.path.dirname(__file__),'template7.jpg')
        save_path = os.path.join(os.path.dirname(__file__),'nowtime.jpg')
        add_text(template_path,save_path,f'{hour_str}点{minute_str}分',textsize=110,textfill='black',position=(260,400))        
	#修改此行调整文字大小位置
    '''
    textsize文字大小
    textfill 文字颜色，black 黑色，blue蓝色，white白色，yellow黄色，red红色
    position是距离图片左上角偏移量，第一个数是宽方向，第二个数是高方向
    f'{hour_str}\n点\n{minute_str}\n分\n了\n !' 代表报时文本，已设置为竖排，\n为换行  
    '''
    base64_str = pic_to_b64(save_path)
    reply = f'[CQ:image,file={base64_str}]'
    await bot.send(event,reply,at_sender=False)

