from PIL import Image

from hoshino.typing import MessageSegment
from ._jielong_data import POSITION, EXPLANATION


JUMP_ID = '-1'
UNKNOWN_ID = '00000'
VALID_IDS = [id for id in POSITION if id != UNKNOWN_ID]
SUB_PIC_SIZE = 80
BASE_PIC_PATH = './hoshino/modules/pcrmemorygames/AtlasMinigameSrtPanel_shrink.png'
BACKGROUND_PIC_PATH = './hoshino/modules/pcrmemorygames/Background.png'


def get_sub_pic_from_id(id, img=Image.open(BASE_PIC_PATH)):
    return img.crop((POSITION[id][0] / 2, POSITION[id][1] / 2, POSITION[id][0] / 2 + POSITION[id][2] / 2,
                        POSITION[id][1] / 2 + POSITION[id][3] / 2))


def generate_full_pic(row_num, col_num, ids, base=None):
    if not base:
        base = Image.new('RGBA', (row_num * SUB_PIC_SIZE, col_num * SUB_PIC_SIZE), (255, 255, 255, 255))
    else:
        base = Image.open(BACKGROUND_PIC_PATH)
    img = Image.open(BASE_PIC_PATH)
    for index, id in enumerate(ids):
        if id == JUMP_ID:
            continue
        row_index = index // col_num
        col_index = index % col_num
        cropped = get_sub_pic_from_id(id, img)
        base.paste(cropped, (col_index * SUB_PIC_SIZE, row_index * SUB_PIC_SIZE))
    return base


def generate_at_message_segment(ulist):
    return ''.join([str(MessageSegment.at(uid)) for uid in ulist])