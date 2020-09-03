# -*- coding:utf-8 -*-

from PIL import ImageDraw, Image, ImageFont
import os,sys
from . import get

absPath = "C:/XCW/hoshino/hoshino/modules/image"
dataPath = "C:/XCW/hoshino/hoshino/modules/image_data"

async def img(text,qq,qun):
    if os.path.exists(absPath+str(qq)+".jpg"):
        os.remove(absPath+str(qq)+".jpg")
    file = await get.getQqName(qq)
    color = await get.getIni(file,"color")
    img = Image.open(dataPath+file+"/"+str(await get.getIni(file,"name"))+".jpg")
    draw = ImageDraw.Draw(img)
    font_size=await get.getIni(file,"font_size")
    font_max=await get.getIni(file,"font_max")
    image_font_center=(await get.getIni(file,"font_center_x"),await get.getIni(file,"font_center_y"))
    image_font_sub = await get.getIni(file,"font_sub")
    ttfront = ImageFont.truetype('simhei.ttf',font_size)  # 设置字体暨字号
    font_length = ttfront.getsize(text)
    #print(font_length)
    while font_length[0]>font_max:
        font_size-=image_font_sub
        ttfront = ImageFont.truetype('simhei.ttf', font_size)
        font_length = ttfront.getsize(text)
    #print(ttfront.getsize("你好"))
    # 自定义打印的文字和文字的位置
    if font_length[0]>5:
        draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                    text, fill=color,font=ttfront)
        picPath = absPath+str(qq)+".jpg"
        img.save(picPath)
        return picPath
