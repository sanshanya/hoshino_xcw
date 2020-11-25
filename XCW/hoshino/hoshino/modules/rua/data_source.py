from os import path

from PIL import Image, ImageDraw

def get_circle_avatar(avatar, size):
    #avatar.thumbnail((size, size))  
    avatar = avatar.resize((size, size))
    scale = 5
    mask = Image.new('L', (size*scale, size*scale), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size * scale, size * scale), fill=255)
    mask = mask.resize((size, size), Image.ANTIALIAS)
    ret_img = avatar.copy()
    ret_img.putalpha(mask)
    return ret_img

def generate_gif(frame_dir: str, avatar: Image.Image) -> Image.Image:
    avatar_size = [(350,350), (438,280), (500,245), (467,263), (350,350)]
    avatar_pos = [(50,150), (40,180), (50,200), (30,180), (50,150)]
    imgs = []
    for i in range(5):
        im = Image.new(mode='RGBA', size=(600, 600), color='white')
        hand = Image.open(path.join(frame_dir, f'hand-{i+1}.png'))
        hand = hand.convert('RGBA')
        avatar = get_circle_avatar(avatar, 350)
        avatar = avatar.resize(avatar_size[i])
        im.paste(avatar, avatar_pos[i], mask=avatar.split()[3])
        im.paste(hand, mask=hand.split()[3])
        imgs.append(im)
    out_path = path.join(frame_dir, 'output.gif')
    imgs[0].save(fp=out_path, save_all=True, append_images=imgs, duration=0.5, loop=0, quality=80)
    return out_path