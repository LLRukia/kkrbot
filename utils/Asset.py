import base64
import os
from io import BytesIO

import globals
from PIL import Image


class ImageAsset:

    cache = {}

    @classmethod
    def get(cls, tag):
        return cls.cache.get(tag, None)

    @classmethod
    def image_path(cls, relative_file_path) -> str:
        if relative_file_path in cls.cache:
            return cls.cache[relative_file_path]
        path = os.path.join(globals.staticpath, relative_file_path)
        im = Image.open(path)
        buf = BytesIO()
        im.save(buf, format)
        raw = f'base64://{str(base64.b64encode(buf.getvalue()), encoding="utf-8")}'
        cls.cache[relative_file_path] = raw
        return raw

    @classmethod
    def image_raw(cls, img: Image.Image, cache_tag=None) -> str:
        if cache_tag:
            if cache_tag in cls.cache:
                return cls.cache[cache_tag]
        buf = BytesIO()
        img.save(buf, format)
        raw = f'base64://{str(base64.b64encode(buf.getvalue()), encoding="utf-8")}'
        if cache_tag:
            cls.cache[cache_tag] = raw
        return raw
