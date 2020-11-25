import requests
import cv2
import numpy
import hoshino
import os
import json
import mimetypes

from io import BytesIO
from PIL import Image
from hoshino.modules.priconne import _pcr_data



logger = hoshino.log.new_logger('avatarguess_killer', hoshino.config.DEBUG)

IMAGES_PATH_STR = hoshino.config.RES_DIR + 'img/priconne/unit/'  # chara icons path
JSON_FILE_PATH_NAME_STR = IMAGES_PATH_STR + 'sprite_chara_icon_name_str_list.json'
SPRITE_IMAGE_SAVE_PATH_STR = IMAGES_PATH_STR + 'sprite.png' 

CHARA_ICON_SIZE_INT = 128  # lenth == height --> TRUE
SPRITE_COLUMN_COUNTS_INT = 15


def get_sprite_chara_icon_name_str_list(update):
    result_message_str = ''
    if os.path.exists(JSON_FILE_PATH_NAME_STR) and update == 'N':
        result_message_str = '已存在json文件,如需更新请使用更新指令,请注意更新前一定要先更新pcr_data。'
        return False, result_message_str
    sprite_chara_icon_name_str_list = []
    chara_id_int_list = _pcr_data.CHARA_NAME.keys()
    try:
        for chara_id_int in chara_id_int_list:
            chara_icon_name_str_list = ['icon_unit_' + str(chara_id_int) + '11.png', 'icon_unit_' + str(chara_id_int) + '31.png', 'icon_unit_' + str(chara_id_int) + '61.png']
            for chara_icon_name_str in chara_icon_name_str_list:
                if os.path.exists(IMAGES_PATH_STR + chara_icon_name_str):
                    sprite_chara_icon_name_str_list.append(chara_icon_name_str)
        with open(JSON_FILE_PATH_NAME_STR,'w') as json_file:
            json.dump(sprite_chara_icon_name_str_list,json_file)
        result_message_str = '生成成功可前往角色头像路径下查看sprite_chara_icon_name_str_list.json'
        return True, result_message_str
    except Exception as exception_str:
        logger.exception(exception_str)
        result_message_str = f'错误：{exception_str}'
        return False, result_message_str

def draw_sprite_image(update):
    result_message_str = ''
    if not os.path.exists(JSON_FILE_PATH_NAME_STR):
        result_message_str = '未生成json文件,请使用指令生成json文件'
        return False, result_message_str
    if os.path.exists(SPRITE_IMAGE_SAVE_PATH_STR) and update == 'N':
        result_message_str = 'sprite图已存在，如需更新请使用更新指令,请注意更新前一定要先更新res下的角色头像图片。'
        return False, result_message_str
    with open(JSON_FILE_PATH_NAME_STR,'r') as json_file:
        sprite_chara_icon_name_str_list = json.load(json_file)
    SPRITE_COLUMN_COUNTS_INT = 15
    images_counts_int = len(sprite_chara_icon_name_str_list)
    sprite_row_counts_int = images_counts_int // SPRITE_COLUMN_COUNTS_INT + 1
    new_sprite_image = Image.new('RGB', (SPRITE_COLUMN_COUNTS_INT * CHARA_ICON_SIZE_INT , sprite_row_counts_int * CHARA_ICON_SIZE_INT))
    try:
        for y_px_int in range(0, sprite_row_counts_int):
            for x_px_int in range(0, SPRITE_COLUMN_COUNTS_INT):
                index = SPRITE_COLUMN_COUNTS_INT * y_px_int + x_px_int
                if index == images_counts_int:
                    break
                chara_icon_image = Image.open(IMAGES_PATH_STR + sprite_chara_icon_name_str_list[index])
                new_sprite_image.paste(chara_icon_image, (x_px_int * CHARA_ICON_SIZE_INT, y_px_int * CHARA_ICON_SIZE_INT))
        new_sprite_image.save(SPRITE_IMAGE_SAVE_PATH_STR)
        result_message_str = '生成成功可前往角色头像路径下查看sprite.png'
        return True,result_message_str
    except Exception as exception_str:
        logger.exception(exception_str)
        result_message_str = f'错误：{exception_str}'
        return False, result_message_str


scale = 1

def search_image_in_another_one(template_image_name):
    sprite_image = cv2.imread(SPRITE_IMAGE_SAVE_PATH_STR)
    sprite_image = cv2.resize(sprite_image, (0, 0), fx=scale, fy=scale)
    template_image = cv2.imread(IMAGES_PATH_STR + template_image_name)
    template_image = cv2.resize(template_image, (0, 0), fx=scale, fy=scale)
    template_size= template_image.shape[:2]
    sprite_gray_image = cv2.cvtColor(sprite_image, cv2.COLOR_BGR2GRAY)
    template_gray_image = cv2.cvtColor(template_image,cv2.COLOR_BGR2GRAY)
    del template_image
    result = cv2.matchTemplate(sprite_gray_image, template_gray_image, cv2.TM_CCOEFF_NORMED)
    del sprite_gray_image, template_gray_image
    threshold = 0.95
    # result >= 95%
    loc = numpy.where(result >= threshold)
    # mark the RGB image by GRAY coordinate
    point = ()
    for pt in zip(*loc[::-1]):
        cv2.rectangle(sprite_image, pt, (pt[0] + template_size[1], pt[1] + + template_size[0]), (7, 249, 151), 2)
        point = pt
    if point==():
        return None,None,None
    return sprite_image,point[0]+ template_size[1] /2,point[1]
    

def transform_coordinate_to_chara_id(template_image_name):
    result_message_str = ''
    if not os.path.exists(JSON_FILE_PATH_NAME_STR):
        result_message_str = '未生成json文件,请使用指令生成json'
        return False, result_message_str
    if not os.path.exists(SPRITE_IMAGE_SAVE_PATH_STR):
        result_message_str = '未生成sprite_image文件,请使用指令生成sprite_image'
        return False, result_message_str
    result_message_str = ''
    image,x_,y_ = search_image_in_another_one(template_image_name)
    if(image is None):
        logger.info("Didn't find result")
        return False, result_message_str
    else:
        logger.info("Coordinate finded:"+str(x_)+" " +str(y_))
    image_index_float = (y_ // CHARA_ICON_SIZE_INT) * SPRITE_COLUMN_COUNTS_INT + (x_ // CHARA_ICON_SIZE_INT)
    with open(JSON_FILE_PATH_NAME_STR,'r') as json_file:
        sprite_chara_icon_name_str_list = json.load(json_file)
    chara_image_name_str = sprite_chara_icon_name_str_list[int(image_index_float)]
    chara_id_int = int(chara_image_name_str.replace('icon_unit_','').replace('11.png','').replace('31.png','').replace('61.png',''))
    return True, chara_id_int
    

    
        
#thank memegenerator plugin
def download_template_image(url:str): 
    try:
        rsp = requests.get(url, stream=True, timeout=5)
        content_type = rsp.headers['Content-Type']
        extension = mimetypes.guess_extension(content_type)
        save_path = os.path.join(IMAGES_PATH_STR, 'template' + extension)
        logger.info(f'Saving template_image to: {save_path}')
        full_file_name = 'template'+extension
    except Exception as e:
        logger.error(f'Failed to download {url}. {type(e)}')
        logger.exception(e)
        return ""
    if 200 == rsp.status_code:
        img = Image.open(BytesIO(rsp.content))
        img.save(save_path)
        logger.info(f'Saved to {save_path}')
        return full_file_name
    else:
        logger.error(f'Failed to download {url}. HTTP {rsp.status_code}')
        return ""
