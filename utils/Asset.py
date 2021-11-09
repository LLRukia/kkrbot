import base64
import os
import random
from glob import glob
from io import BytesIO

import globals
from PIL import Image


class ImageAsset:

    cache = {}

    preset = {
        '粉键': ['kkr/pink_note.jpg'],
        'gkd': ['kkr/gkd.jpg'],
        '沉船': ['abaaba.jpg'],
        '氪': ['abaaba.jpg', 'kkr/starstone.jpg'],
        '太强了': ['kkr/tql.jpg'],
        '太强啦': ['kkr/tql.jpg'],
        'tql': ['kkr/tql.jpg'],
        '憨批': ['kkr/haha.jpg', 'kkr/haha_hanpi.jpg', 'kkr/r_u_hanpi.png'],
        '牛逼': ['kkr/nb.jpg'],
        'nb': ['kkr/nb.jpg'],
        '去世': ['kkr/grey.jpg'],
        '吐血': ['kkr/grey.jpg'],
        '震撼': ['kkr/autumn_stunned.jpg', 'kkr/stunned.jpg', 'kkr/stunned2.jpg', 'kkr/amazed.gif'],
        '想要': ['kkr/want.jpg'],
        '嘿嘿': ['kkr/Halloween_heihei.gif', 'kkr/heihei.gif'],
        '震惊': ['kkr/autumn_stunned.jpg', 'kkr/stunned.jpg', 'kkr/stunned2.jpg', 'kkr/amazed.gif'],
        '唱歌': ['kkr/singing.gif'],
        '自爆': ['kkr/rocket.gif'],
        '哦哦哦': ['kkr/poke.gif'],
    }

    @classmethod
    def random_preset_image(cls, preset_tag):
        return f'file:///{os.path.abspath(os.path.join(globals.staticpath, random.choice(cls.preset[preset_tag])))}'

    @classmethod
    def get(cls, tag):
        return cls.cache.get(tag, None)

    @classmethod
    def static_image(cls, relative_file_path) -> str:
        return f'file:///{os.path.abspath(os.path.join(globals.staticpath, relative_file_path))}'

    @classmethod
    def image_path(cls, file_path) -> str:
        return f'file:///{file_path}'

    @classmethod
    def image_raw(cls, im: Image.Image, cache_tag=None, format='PNG') -> str:
        if cache_tag:
            if cache_tag in cls.cache:
                return cls.cache[cache_tag]
        buf = BytesIO()
        im.save(buf, format=format)
        raw = f'base64://{str(base64.b64encode(buf.getvalue()), encoding="utf-8")}'
        if cache_tag:
            cls.cache[cache_tag] = raw
        return raw
