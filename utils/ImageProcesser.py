import os
import re
import uuid

import globals
from PIL import Image, ImageDraw, ImageFont
from utils.Asset import ImageAsset

SPACING = 5
back_regex = re.compile(r'back_([0-9]*)\.jpg')
BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT = 140, 130
BACK_PIC_NUM_EACH_LINE = 5


def bg_image_gen(back_number, s):
    def half_en_len(s):
        return (len(s) + (len(s.encode(encoding='utf-8')) - len(s)) // 2) // 2
    back_number = f'back_{back_number}'
    img_path = os.path.join(globals.staticpath, f'bg/{back_number}.jpg')
    im_src = Image.open(img_path)
    if back_number in [f'back_{n}' for n in [38, 46, 47, 51, 52, 53]]:
        real_width = max(3, im_src.width // max(6, half_en_len(s)) * 4 // 5)
        font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), real_width)
        real_height = real_width + SPACING
        im = Image.new('RGB', (im_src.width, im_src.height), (255, 255, 255))
        im.paste(im_src)
        text_width = im_src.width

        draw = ImageDraw.Draw(im)
        sz = draw.textsize(s, font=font)
        x = (text_width - sz[0]) / 2
        y = im_src.height - real_height
        draw.text((x, y), s, fill=(245, 255, 250), font=font)
    elif back_number in [f'back_{n}' for n in [33]]:
        real_width = max(3, im_src.width // max(6, half_en_len(s)) * 4 // 5)
        font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), real_width)
        real_height = real_width + SPACING
        im = Image.new('RGB', (im_src.width, im_src.height), (255, 255, 255))
        im.paste(im_src)
        text_width = im_src.width
        draw = ImageDraw.Draw(im)
        sz = draw.textsize(s, font=font)
        x = (text_width - sz[0]) / 2
        y = im_src.height - 2 * real_height
        draw.text((x, y), s, fill=(245, 255, 250), font=font)
    elif back_number in [f'back_{n}' for n in [50]]:
        real_width = max(3, im_src.width // max(6, half_en_len(s)) * 4 // 5)
        font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), real_width)
        real_height = real_width + SPACING
        im = Image.new('RGB', (im_src.width, im_src.height), (255, 255, 255))
        im.paste(im_src)
        text_width = im_src.width

        draw = ImageDraw.Draw(im)
        sz = draw.textsize(s, font=font)
        x = (text_width - sz[0]) / 2
        y = 5
        draw.text((x, y), s, fill=(23, 0, 0), font=font)
    else:
        real_width = max(3, im_src.width // max(6, half_en_len(s)))
        font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), real_width)
        real_height = real_width + SPACING
        im = Image.new('RGB', (im_src.width, im_src.height + real_height), (255, 255, 255))
        im.paste(im_src)
        text_width = im_src.width

        draw = ImageDraw.Draw(im)
        sz = draw.textsize(s, font=font)
        x = (text_width - sz[0]) / 2
        y = im_src.height
        draw.text((x, y), s, fill=(23, 0, 0), font=font)
    return im


def get_back_pics():
    raw = ImageAsset.get('back_catalogue')
    if raw:
        return raw

    back_pic_set = set()
    for _, _, files in os.walk(os.path.join(globals.staticpath, 'bg')):
        for f in files:
            if f.startswith('back_') and f.endswith('.jpg'):
                num = int(back_regex.findall(f)[0])
                back_pic_set.add(num)

    cur_back_pic_nums = len(back_pic_set)
    if cur_back_pic_nums == 0:
        return

    im = Image.new('RGB', (BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT * (((cur_back_pic_nums - 1) // BACK_PIC_NUM_EACH_LINE) + 1)), (255, 255, 255))
    for i, num in enumerate(back_pic_set):
        im_o = bg_image_gen(num, f'底图 {num}')
        im_o = im_o.resize((BACK_PIC_UNIT_WIDTH, BACK_PIC_UNIT_HEIGHT))
        box = (i % BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_WIDTH, i // BACK_PIC_NUM_EACH_LINE * BACK_PIC_UNIT_HEIGHT)
        im.paste(im_o, box)

    return ImageAsset.image_raw(im, 'back_catalogue')


def merge_image(rsn, rarity, attribute, band_id, thumbnail=True, trained=False, return_fn=False):
    if thumbnail:
        try:
            if return_fn:
                fn = os.path.join(globals.datapath, 'image', f'auto_reply/cards/thumb/m_{rsn}_{"normal" if not trained else "after_training"}.png')
                if os.access(fn, os.R_OK):
                    return fn
            attribute_icon = Image.open(os.path.join(globals.asset_resource_path, f'{attribute}.png'))
            band_icon = Image.open(os.path.join(globals.asset_resource_path, f'band_{band_id}.png'))
            if not trained:
                back_image = Image.open(f'{os.path.join(globals.asset_card_thumb_path, f"{rsn}_normal.png")}')
                star = Image.open(os.path.join(globals.asset_resource_path, 'star.png')).resize((32, 32), Image.ANTIALIAS)
            else:
                back_image = Image.open(f'{os.path.join(globals.asset_card_thumb_path, f"{rsn}_after_training.png")}')
                star = Image.open(os.path.join(globals.asset_resource_path, 'star_trained.png')).resize((32, 32), Image.ANTIALIAS)
            if rarity == 1:
                frame = Image.open(os.path.join(globals.asset_resource_path, f'card-1-{attribute}.png'))
            else:
                frame = Image.open(os.path.join(globals.asset_resource_path, f'card-{rarity}.png'))

            back_image.paste(frame, (0, 0), mask=frame)
            back_image.paste(band_icon, (0, 0), mask=band_icon)
            back_image.paste(attribute_icon, (180 - 50, 0), mask=attribute_icon)
            for i in range(rarity):
                back_image.paste(star, (2, 170 - 27 * (i + 1)), mask=star)
            if return_fn:
                fn = os.path.join(globals.datapath, 'image', f'auto_reply/cards/thumb/m_{rsn}_{"normal" if not trained else "after_training"}.png')
                back_image.save(fn)
                return fn
            return back_image
        except:
            import sys
            sys.excepthook(*sys.exc_info())
            return None

    else:
        fn = os.path.join(globals.datapath, 'image', f'auto_reply/cards/m_{rsn}_{"normal" if not trained else "after_training"}.png')
        if os.access(fn, os.R_OK):
            return fn

        try:
            OUT_WIDTH, OUT_HEIGHT = 1364, 1020
            INNER_WIDTH, INNER_HEIGHT = 1334, 1002
            STAR_SIZE, ICON_SIZE = 100, 150
            TOP_OFFSET, RIGHT_OFFSET, BOTTOM_OFFSET, LEFT_OFFSET = 22, 165, 20, 10
            STAT_STEP = 95

            back_image = Image.new('RGB', (OUT_WIDTH, OUT_HEIGHT))
            attribute_icon = Image.open(os.path.join(globals.asset_resource_path, f'{attribute}.png')).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
            band_icon = Image.open(os.path.join(globals.asset_resource_path, f'band_{band_id}.png')).resize((ICON_SIZE, ICON_SIZE), Image.ANTIALIAS)
            if not trained:
                card = Image.open(f'{os.path.join(globals.asset_card_path, f"{rsn}_card_normal.png")}')
                star = Image.open(os.path.join(globals.asset_resource_path, 'star.png')).resize((STAR_SIZE, STAR_SIZE), Image.ANTIALIAS)
            else:
                card = Image.open(f'{os.path.join(globals.asset_card_path, f"{rsn}_card_after_training.png")}')
                star = Image.open(os.path.join(globals.asset_resource_path, 'star_trained.png')).resize((STAR_SIZE, STAR_SIZE), Image.ANTIALIAS)
            if rarity == 1:
                frame = Image.open(os.path.join(globals.asset_resource_path, f'frame-1-{attribute}.png')).resize((OUT_WIDTH, OUT_HEIGHT), Image.ANTIALIAS)
            else:
                frame = Image.open(os.path.join(globals.asset_resource_path, f'frame-{rarity}.png')).resize((OUT_WIDTH, OUT_HEIGHT), Image.ANTIALIAS)

            back_image.paste(card, ((OUT_WIDTH - INNER_WIDTH) // 2, (OUT_HEIGHT - INNER_HEIGHT) // 2), mask=card)
            back_image.paste(frame, (0, 0), mask=frame)
            back_image.paste(band_icon, (LEFT_OFFSET, TOP_OFFSET), mask=band_icon)
            back_image.paste(attribute_icon, (OUT_WIDTH - RIGHT_OFFSET, TOP_OFFSET), mask=attribute_icon)
            for i in range(rarity):
                back_image.paste(star, (LEFT_OFFSET, OUT_HEIGHT - BOTTOM_OFFSET - STAT_STEP * (i + 1)), mask=star)
            back_image.save(fn)
            return fn
        except:
            return ''


def white_padding(width, height):
    return Image.new('RGB', (width, height), (255, 255, 255))


def thumbnail(**options):
    # images: a list of Image objects, or a list of lists(tuples) of Image objects
    # labels: a list of strings shown at the bottom
    # image_style: if not assigned, take the params of the first image; if both assigned, will be forced to resize
    # width: width of each image, if not assigned, will be min(scaled value by height, 180)
    # height: height of each image, if not assigned, will be min(scaled value by width, 180)
    # label_style:
    # font_size: font_size of each label
    # col_num (images are arranged row by row)
    # col_space: (space between two columns)
    # row_space (space between two rows, if labels exist, it means the space between the label of row1 and the image of row2)
    images = options['images']
    first_image = images[0]
    if not isinstance(first_image, Image.Image):
        if isinstance(first_image, (list, tuple)):
            first_image = first_image[0]
            if not isinstance(first_image, Image.Image):
                raise Exception('images must be a list of Image objects, or a list of lists(tuples) of Image objects')
        else:
            raise Exception('images must be a list of Image objects, or a list of lists(tuples) of Image objects')
    else:
        images = [[im] for im in images]

    if not options.get('image_style'):
        box_width, box_height = first_image.size
    else:
        if options['image_style'].get('width') and options['image_style'].get('height'):
            box_width, box_height = options['image_style']['width'], options['image_style']['height']
            images = [[im.resize((box_width, box_height)) for im in im_list] for im_list in images]
        elif options['image_style'].get('width') and not options['image_style'].get('height'):
            images = [[im.resize((options['image_style']['width'], options['image_style']['width'] * im.size[1] // im.size[0])) for im in im_list] for im_list in images]
            box_width, box_height = options['image_style']['width'], max([im.size[1] for im_list in images for im in im_list])
        elif not options['image_style'].get('width') and options['image_style'].get('height'):
            images = [[im.resize((options['image_style']['height'] * im.size[0] // im.size[1], options['image_style']['height'])) for im in im_list] for im_list in images]
            box_width, box_height = max([im.size[0] for im_list in images for im in im_list]), options['image_style']['height']

    col_num = options.get('col_num', 4)
    row_num = (len(images) - 1) // col_num + 1
    col_space = options.get('col_space', 0)
    row_space = options.get('row_space', 0)

    if options.get('labels'):
        font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), options.get('label_style', {}).get('font_size', 20))
        all_chars = set()
        max_label_width = 0
        for label in options['labels']:
            max_label_width = max(max_label_width, ImageDraw.Draw(Image.new('RGB', (0, 0))).textsize(label, font=font)[0])
            all_chars |= set(label)
        label_height = ImageDraw.Draw(Image.new('RGB', (0, 0))).textsize(''.join(all_chars), font=font)[1]
        box_width = max(box_width * len(images[0]), max_label_width) // len(images[0])

        back_image = Image.new('RGB', (
            col_num * len(images[0]) * box_width + (col_num - 1) * col_space,
            (box_height + label_height) * row_num + row_num * row_space,
        ), (255, 255, 255))

        draw = ImageDraw.Draw(back_image)
        labels = options['labels']
        for r in range(row_num):
            for c in range(col_num):
                if r * col_num + c >= len(images):
                    break
                image_group = images[r * col_num + c]
                for i, im in enumerate(image_group):
                    back_image.paste(im, (
                        (len(image_group) * c + i) * box_width + (box_width - im.size[0]) // 2 + col_space * c,
                        r * (box_height + label_height + row_space)
                    ))
                sz = draw.textsize(labels[r * col_num + c], font=font)
                draw.text((
                    len(image_group) * c * box_width + (len(image_group) * box_width - sz[0]) // 2 + c * col_space, r * (box_height + label_height + row_space) + box_height
                ), labels[r * col_num + c], fill=(0, 0, 0), font=font)
    else:
        back_image = Image.new('RGB', (
            col_num * len(images[0]) * box_width + (col_num - 1) * col_space,
            box_height * row_num + (row_num - 1) * row_space
        ), (255, 255, 255))

        draw = ImageDraw.Draw(back_image)
        for r in range(row_num):
            for c in range(col_num):
                if r * col_num + c >= len(images):
                    break
                image_group = images[r * col_num + c]
                for i, im in enumerate(image_group):
                    back_image.paste(im, (
                        (len(image_group) * c + i) * box_width + (box_width - im.size[0]) // 2 + c * col_space * int(i == len(image_group) - 1),
                        r * (box_height + row_space)
                    ))

    return ImageAsset.image_raw(back_image)


def open_nontransparent(filename):
    try:
        image = Image.open(filename).convert('RGBA')
        new_image = Image.new('RGBA', image.size, (255, 255, 255, 255))
        new_image.paste(image, (0, 0), image)
        return new_image
    except:
        pass


def str_to_pic(lines = [], tag = None):
    if tag:
        raw = ImageAsset.get(tag)
        if raw:
            return raw

    if not lines:
        return None

    row_space = 20
    col_space = 50
    font = ImageFont.truetype(os.path.join(globals.staticpath, 'simhei.ttf'), 20)

    line_height = ImageDraw.Draw(Image.new('RGB', (0, 0))).textsize('底图目录', font=font)[1]

    image = Image.new('RGB', (ImageDraw.Draw(Image.new('RGB', (0, 0))).textsize(max(lines, key=lambda line: len(line)),
                      font=font)[0] + 2 * col_space, (line_height + row_space) * len(lines)), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    line_pos = row_space

    for i, line in enumerate(lines):
        sz = draw.textsize(line, font=font)
        draw.text((col_space, line_pos), line, fill=(0, 0, 0), font=font)
        line_pos += sz[1] + row_space

    return ImageAsset.image_raw(image, tag)


def compress(infile, mb=None, step=10, quality=80, isabs=False):
    if not isabs:
        absinfile = os.path.join(globals.datapath, 'image', infile)
    else:
        absinfile = infile
    outfile = infile[infile.rfind('/') + 1:infile.rfind('.')] + '-c.jpg'
    absoutfile = os.path.join(globals.datapath, 'image', outfile)
    if os.path.exists(absoutfile):
        return outfile
    if mb is None:
        im = Image.open(absinfile)
        im = im.convert('RGB')
        im.save(absoutfile, quality=quality)
        return absoutfile

    o_size = os.path.getsize(absinfile) / 1024
    if o_size <= mb:
        return infile

    while o_size > mb:
        im = Image.open(absinfile)
        im = im.convert('RGB')
        im.save(absoutfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = os.path.getsize(absoutfile) / 1024
    return absoutfile
