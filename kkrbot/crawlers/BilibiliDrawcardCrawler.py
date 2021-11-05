import functools
import os
import pickle
import time

import globals
import httpx


class RollbackError(Exception):
    def __init__(self, new, old):
        self.new = new
        self.old = old

    def __str__(self):
        return f'Data rollback: new {self.new} = old {self.old}'


class BilibiliDrawcardCrawler:

    SAVEFILE = os.path.join(globals.config.datapath, 'save.pickle')

    def __init__(self):
        self._gacha_dict = {}
        if not os.path.exists(self.SAVEFILE):
            self._data = []
        else:
            self._data = self._load_data(self.SAVEFILE)

    def _save_data(self, filename, data):
        try:
            tempname = filename + '.tmp'
            with open(tempname, 'wb') as f:
                pickle.dump(data, f)
            os.replace(tempname, filename)
        except OSError:
            import sys
            sys.excepthook(*sys.exc_info())

    def _load_data(self, filename):
        out = []
        try:
            with open(filename, 'rb') as f:
                out = pickle.load(f)
        except OSError:
            import sys
            sys.excepthook(*sys.exc_info())
        return out

    async def fetch_once(self):
        try:
            self._gacha_dict = await self._fetch_json_from_bestdori()
        except:
            import sys
            sys.excepthook(*sys.exc_info())
        try:
            lastitems = self._data[-10000:] if self._data else None
            new_data = await self._spider(lastitems)
            if len(new_data) > 100:
                pass
            self._data.extend(new_data)
            self._save_data(self.SAVEFILE, self._data)
            return len(new_data)
        except RollbackError as e:
            globals.logger.warning(e)
        except:
            import sys
            sys.excepthook(*sys.exc_info())
        return 0

    async def _spider(self, lastitems=None):
        rawdata = await self._request_page(1, 10000)
        items = self._stripe_data(rawdata)
        if len(items) == 0:
            raise ValueError('Empty data')
        # find match
        if lastitems:
            for i, item in enumerate(items):
                if self._is_equal(item, lastitems[-1]):
                    items = items[:i]
                    break
                for j, _ in enumerate(lastitems):
                    raise RollbackError(i, len(lastitems) - j - 1)
        items.reverse()
        return items

    async def _request_page(self, page=1, limit=20):
        params = {
            'page': page,
            'limit': limit,
            '_': int(time.time() * 1000)
        }
        async with httpx.AsyncClient() as client:
            r = await client.get('https://qcloud-sdkact-api.biligame.com/bangdream/h5/user/situation/all', params=params, timeout=20)
            r.raise_for_status()
            j = r.json()
            if j['code'] != 0:
                raise ValueError(j['code'], j.get('message'))
            return j['data']

    def _stripe_data(self, data):
        data = data['data']
        out = []
        for rawitem in data:
            item = {
                'card': rawitem['situation_id'],
                'gacha': rawitem['gacha_id'],
                'uid': rawitem['user_id'],
                'uname': rawitem['user_name'],
                'ts': rawitem['gacha_at'],
            }
            out.append(item)
        return out

    @staticmethod
    def _is_equal(a, b):
        return (
            a['ts'] == b['ts'] and
            a['uid'] == b['uid'] and
            a['card'] == b['card'] and
            a['gacha'] == b['gacha']
        )

    def get_data_by_user(self, user):
        ret = filter(lambda i: user in i['uname'], self._data)
        for i in ret:
            i['gacha'] = self.get_gacha_name(i['gacha'])
        return ret

    async def _fetch_json_from_bestdori(self, url):
        async with httpx.AsyncClient() as client:
            r = await client.get('https://bestdori.com/api/gacha/all.5.json', timeout=20)
            r.raise_for_status()
            return r.json()

    def get_gacha_name(self, gacha):
        gacha_info = self._gacha_dict.get(str(gacha), None)
        if gacha_info is None:
            return ''
        namelist = gacha_info.get('gachaName', [])
        return self._locale_chinese(namelist, 3)

    @staticmethod
    def _locale_chinese(li, chinese_index, default=''):
        if chinese_index < len(li) and li[chinese_index]:
            return li[chinese_index]
        for name in li:
            if name:
                return name
        return default


drawcard_crawler = BilibiliDrawcardCrawler()
