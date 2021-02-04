from PIL import ImageFont, ImageDraw, Image
from hoshino import Service,R,priv
from hoshino.util import pic2b64
sv_help = '''
高情商
'''.strip()

offset_x = 270

sv = Service(
    name = '高情商',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #是否可见
    enable_on_default = True, #是否默认启用
    bundle = '通用', #属于哪一类
    help_ = sv_help #帮助文本
    )

@sv.on_fullmatch(["帮助高情商"])
async def bangzhu(bot, ev):
    await bot.send(ev, sv_help, at_sender=True)

fontpath=R.img('priconne/fronts/FZY3K.TTF').path
path = R.img('high_eq_image.png').path
def draw_text(img_pil, text, offset_x):
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(fontpath, 36)
    width, height = draw.textsize(text, font)
    x = 5
    if width > 900:
        font = ImageFont.truetype(fontpath, int(200 * 36 / width))
        width, height = draw.textsize(text, font)
    else:
        x = int((360 - width) / 2)
    draw.rectangle((x + offset_x - 2, 360, x + 2 + width + offset_x, 360 + height * 1.2), fill=(0, 0, 0, 255))
    draw.text((x + offset_x, 360), text, font=font, fill=(255, 255, 255, 255))
@sv.on_rex(r'低情商(.+)高情商(.+)', normalize=True)
async def low_eq(bot,ev):
    match = ev['match']
    left = match.group(1).strip().strip(":").strip("。")
    right = match.group(2).strip().strip(":").strip("。")
    if len(left) > 15 or len(right) > 15:
        await bot.send(ev,"为了图片质量，请不要多于15个字符")
        return
    img_p = Image.open(path)
    draw_text(img_p, left, -24)
    draw_text(img_p, right, offset_x)
    await bot.send(ev,f'[CQ:image,file={pic2b64(img_p)}]')
@sv.on_rex(r'高情商(.+)低情商(.+)', normalize=True)
async def high_eq(bot,ev):
    match = ev['match']
    left = match.group(1).strip().strip(":").strip("。")
    right = match.group(2).strip().strip(":").strip("。")
    if len(left) > 15 or len(right) > 15:
        await bot.send(ev,"为了图片质量，请不要多于15个字符")
        return
    img_p = Image.open(path)
    draw_text(img_p, right, -24)
    draw_text(img_p, left, offset_x)
    await bot.send(ev,f'[CQ:image,file={pic2b64(img_p)}]')