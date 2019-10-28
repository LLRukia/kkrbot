import os
import re
import uuid

import const
from PIL import Image, ImageDraw, ImageFont

SPACING = 5
FONT = 'cache/simhei.ttf'
back_regex = re.compile(r'back_([0-9]*)\.jpg')
CUR_BACK_PIC_SET = set()
BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT = 140, 130
BACK_PIC_NUM_EACH_LINE = 5

def image_merge(back_number, s, get_im_obj=False):
    back_number = 'back_%d' % back_number
    filename = '%s.jpg' % s
    path = os.path.join(const.datapath, f'image/auto_reply/{back_number}/%s' % filename)
    if os.access(path, os.R_OK):
        return f'auto_reply/{back_number}/%s' % filename
    img_path = os.path.join(const.cachepath, f'{back_number}.jpg')
    im_src = Image.open(img_path)
    real_width = max(3, im_src.width // max(6, len(s)))
    font = ImageFont.truetype(os.path.join(const.workpath, FONT), real_width)
    real_height = real_width + SPACING
    im = Image.new('RGB', (im_src.width, im_src.height + real_height), (255,255,255))
    im.paste(im_src)
    text_width = im_src.width

    draw = ImageDraw.Draw(im)
    sz = draw.textsize(s, font=font)
    x = (text_width - sz[0]) / 2
    y = im_src.height
    draw.text((x, y), s, fill=(23, 0, 0), font=font)
    if get_im_obj:
        return im
    else:
        im.save(path)
        return f'auto_reply/{back_number}/%s' % filename

def get_back_pics():
    return 'auto_reply/back_catalogue.jpg'

def init():
    global CUR_BACK_PIC_SET
    for _, _, files in os.walk(os.path.join(const.workpath, 'cache')):
        for f in files:
            if f.startswith('back_') and f.endswith('.jpg'):
                num = int(back_regex.findall(f)[0])
                CUR_BACK_PIC_SET.add(num)
    
    cur_back_pic_nums = len(CUR_BACK_PIC_SET)

    im = Image.new('RGB', (BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT * (((cur_back_pic_nums - 1) // BACK_PIC_NUM_EACH_LINE) + 1)), (255,255,255))
    for i, num in enumerate(CUR_BACK_PIC_SET):
        im_o = image_merge(num, '底图 %d' % num, get_im_obj=True)
        im_o = im_o.resize((BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT))
        box = (i % BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_WIDTH, i // BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_HEIGHT)
        im.paste(im_o, box)
    im.save(os.path.join(const.datapath, f'image/auto_reply/back_catalogue.jpg'))
    

init()

def thumbnail(images: list, texts: list):
    N_COLS = 4
    N_ROWS = (len(images) - 1) // N_COLS + 1
    
    FONT_SIZE = 20
    WIDTH = 180
    HEIGHT = 180
    font = ImageFont.truetype(os.path.join(const.workpath, FONT), FONT_SIZE)
    im = Image.new('RGB', (WIDTH * N_COLS, (HEIGHT + FONT_SIZE) * N_ROWS), (255,255,255))
    draw = ImageDraw.Draw(im)

    for r in range(N_ROWS):
        for c in range(N_COLS):
            if r * N_COLS + c >= len(images):
                break
            im.paste(images[r * N_COLS + c], (c * WIDTH, r * (HEIGHT + FONT_SIZE)))
            sz = draw.textsize(texts[r * N_COLS + c], font=font)
            draw.text((c * WIDTH + WIDTH // 2 - sz[0] // 2, r * (HEIGHT + sz[1]) + HEIGHT), str(texts[r * N_COLS + c]), fill=(0,0,0), font=font)
    
    fn = f'{str(uuid.uuid1())}.jpg'
    im.save(os.path.join(const.datapath, 'image', fn))
    return fn

def thumbnail2(images: list, images_trained: list, texts: list):
    N_COLS = 4
    N_ROWS = (len(images) - 1) // N_COLS + 1
    
    FONT_SIZE = 20
    WIDTH = 180
    HEIGHT = 180
    font = ImageFont.truetype(os.path.join(const.workpath, FONT), FONT_SIZE)
    text_height = ImageDraw.Draw(Image.new('RGB', (1, 1))).textsize('0123456789&|分判奶盾()', font=font)[1]
    im = Image.new('RGB', (2 * WIDTH * N_COLS, (HEIGHT + text_height) * N_ROWS), (255,255,255))
    draw = ImageDraw.Draw(im)

    for r in range(N_ROWS):
        for c in range(N_COLS):
            if r * N_COLS + c >= len(images):
                break
            im.paste(images[r * N_COLS + c], (2 * c * WIDTH, r * (HEIGHT + text_height)))
            im.paste(images_trained[r * N_COLS + c], (2 * c * WIDTH + WIDTH, r * (HEIGHT + text_height)))
            sz = draw.textsize(texts[r * N_COLS + c], font=font)
            draw.text((2 * c * WIDTH + WIDTH - sz[0] // 2, r * (HEIGHT + text_height) + HEIGHT), str(texts[r * N_COLS + c]), fill=(0,0,0), font=font)
    
    fn = f'{str(uuid.uuid1())}.jpg'
    im.save(os.path.join(const.datapath, 'image', fn))
    return fn

def merge_image(rsn, rarity, attribute, band_id, thumbnail=True, trained=False):
    if thumbnail:
        try:
            attribute_icon = Image.open(os.path.join(const.resourcepath, f'{attribute}.png'))
            band_icon = Image.open(os.path.join(const.resourcepath, f'band_{band_id}.png'))
            if not trained:
                back_image = Image.open(f'{os.path.join(const.thumbnailpath, f"{rsn}_normal.png")}')
                star = Image.open(os.path.join(const.resourcepath, 'star.png')).resize((32, 32), Image.ANTIALIAS)
            else:
                back_image = Image.open(f'{os.path.join(const.thumbnailpath, f"{rsn}_after_training.png")}')
                star = Image.open(os.path.join(const.resourcepath, 'star_trained.png')).resize((32, 32), Image.ANTIALIAS)
            if rarity == 1:
                frame = Image.open(os.path.join(const.resourcepath, f'card-1-{attribute}.png'))
            else:
                frame = Image.open(os.path.join(const.resourcepath, f'card-{rarity}.png'))
            
            back_image.paste(frame, (0, 0), mask=frame)
            back_image.paste(band_icon, (0, 0), mask=band_icon)
            back_image.paste(attribute_icon, (180 - 50, 0), mask=attribute_icon)
            for i in range(rarity):
                back_image.paste(star, (2, 170 - 27 * (i + 1)), mask=star)
            return back_image
        except:
            return None

    else:
        fn = f'auto_reply/cards/m_{rsn}_{"normal" if not trained else "after_training"}.png'
        if os.access(os.path.join(const.datapath, 'image', fn), os.R_OK):
            return fn
        
        try:
            OUT_WIDTH, OUT_HEIGHT = 1364, 1020
            INNER_WIDTH, INNER_HEIGHT = 1334, 1002
            STAR_SIZE, ICON_SIZE = 100, 150
            TOP_OFFSET, RIGHT_OFFSET, BOTTOM_OFFSET, LEFT_OFFSET = 22, 165, 20, 10
            STAT_STEP = 95

            back_image = Image.new('RGB', (OUT_WIDTH, OUT_HEIGHT))
            attribute_icon = Image.open(os.path.join(const.resourcepath, f'{attribute}.png')).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
            band_icon = Image.open(os.path.join(const.resourcepath, f'band_{band_id}.png')).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
            if not trained:
                card = Image.open(f'{os.path.join(const.assetpath, f"{rsn}_card_normal.png")}')
                star = Image.open(os.path.join(const.resourcepath, 'star.png')).resize((STAR_SIZE, STAR_SIZE), Image.ANTIALIAS)
            else:
                card = Image.open(f'{os.path.join(const.assetpath, f"{rsn}_card_after_training.png")}')
                star = Image.open(os.path.join(const.resourcepath, 'star_trained.png')).resize((STAR_SIZE, STAR_SIZE), Image.ANTIALIAS)
            if rarity == 1:
                frame = Image.open(os.path.join(const.resourcepath, f'frame-1-{attribute}.png')).resize((OUT_WIDTH, OUT_HEIGHT), Image.ANTIALIAS)
            else:
                frame = Image.open(os.path.join(const.resourcepath, f'frame-{rarity}.png')).resize((OUT_WIDTH, OUT_HEIGHT), Image.ANTIALIAS)

            back_image.paste(card, ((OUT_WIDTH - INNER_WIDTH) // 2, (OUT_HEIGHT - INNER_HEIGHT) // 2), mask=card)
            back_image.paste(frame, (0, 0), mask=frame)
            back_image.paste(band_icon, (LEFT_OFFSET, TOP_OFFSET), mask=band_icon)
            back_image.paste(attribute_icon, (OUT_WIDTH - RIGHT_OFFSET, TOP_OFFSET), mask=attribute_icon)
            for i in range(rarity):
                back_image.paste(star, (LEFT_OFFSET, OUT_HEIGHT - BOTTOM_OFFSET - STAT_STEP * (i + 1)), mask=star)
            back_image.save(os.path.join(const.datapath, 'image', fn))
            return fn
        except:
            return ''
        

def white_padding(width, height):
    return Image.new('RGB', (width, height), (255, 255, 255))
