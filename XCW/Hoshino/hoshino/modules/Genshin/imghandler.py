from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
from hoshino import aiorequests
from io import BytesIO


async def get_pic(url, size=None, *args, **kwargs) -> Image:
    """
    从网络获取图片，格式化为RGBA格式的指定尺寸
    """
    resp = await aiorequests.get(url, stream=True, *args, **kwargs)
    if resp.status_code != 200:
        return None
    pic = Image.open(BytesIO(await resp.content))
    pic = pic.convert("RGBA")
    if size is not None:
        pic = pic.resize(size, Image.LANCZOS)
    return pic


def easy_paste(im: Image, im_paste: Image, pos=(0, 0), direction="lt"):
    """
    inplace method
    快速粘贴, 自动获取被粘贴图像的坐标。
    pos应当是粘贴点坐标，direction指定粘贴点方位，例如lt为左上
    """
    x, y = pos
    size_x, size_y = im_paste.size
    if "d" in direction:
        y = y - size_y
    if "r" in direction:
        x = x - size_x
    if "c" in direction:
        x = x - int(0.5 * size_x)
        y = y - int(0.5 * size_y)
    im.paste(im_paste, (x, y, x + size_x, y + size_y), im_paste)


def easy_alpha_composite(im: Image, im_paste: Image, pos=(0, 0), direction="lt") -> Image:
    '''
    透明图像快速粘贴
    '''
    base = Image.new("RGBA", im.size)
    easy_paste(base, im_paste, pos, direction)
    base = Image.alpha_composite(im, base)
    return base


def draw_text_by_line(img, pos, text, font, fill, max_length, center=False, line_space=None):
    """
    在图片上写长段文字, 自动换行
    max_length单行最大长度, 单位像素
    line_space  行间距, 单位像素, 默认是字体高度的0.3倍
    """
    x, y = pos
    _, h = font.getsize("X")
    if line_space is None:
        y_add = math.ceil(1.3 * h)
    else:
        y_add = math.ceil(h + line_space)
    draw = ImageDraw.Draw(img)
    row = ""  # 存储本行文字
    length = 0  # 记录本行长度  
    for character in text:
        w, h = font.getsize(character)  # 获取当前字符的宽度
        if length + w * 2 <= max_length:
            row += character
            length += w
        else:
            row += character
            if center:
                font_size = font.getsize(row)
                x = math.ceil((img.size[0] - font_size[0]) / 2)
            draw.text((x, y), row, font=font, fill=fill)
            row = ""
            length = 0
            y += y_add
    if row != "":
        if center:
            font_size = font.getsize(row)
            x = math.ceil((img.size[0] - font_size[0]) / 2)
        draw.text((x, y), row, font=font, fill=fill)


def image_array(canvas, image_list, col, space=0, top=0):
    '''
    循环贴图到画布

    canvas：画布

    image_list：图片列表，应大小一致

    col：竖列数量

    space：图片间距

    top：顶部间距
    '''
    num = list(range(len(image_list)))
    column = 0
    x = 0
    y = 0
    for i, image in zip(num, image_list):
        i += 1
        rows = math.ceil(i / col) - 1
        x = column * (image.size[0] + space)
        y = top + rows * (image.size[1] + space)
        column += 1
        if column == col:
            column = 0
        if i == len(image_list):
            x = col * (image.size[0] + space) - space
            y += image.size[1]
    list_canvas = Image.new('RGBA', (x, y), (255, 255, 255, 0))
    column = 0
    for i, image in zip(num, image_list):
        i += 1
        rows = math.ceil(i / col) - 1
        x = column * (image.size[0] + space)
        y = top + rows * (image.size[1] + space)
        column += 1
        easy_paste(list_canvas, image, (x, y))
        if column == col:
            column = 0
    easy_paste(canvas, list_canvas, (math.ceil((canvas.size[0] - list_canvas.size[0]) / 2), 0))
    return canvas
