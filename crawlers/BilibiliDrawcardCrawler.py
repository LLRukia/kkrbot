import os
import pickle
import time

import globals
import httpx


class DrawCard_Item:
    def __init__(self, rawitem):
        self.situation_id = int(rawitem['situation_id'])
        self.gacha_name = rawitem['gacha_name']
        self.user_id = int(rawitem['user_id'])
        self.user_name = rawitem['user_name']
        self.gacha_at = int(rawitem['gacha_at'])
        self.gacha_id = int(rawitem['gacha_id'])

    def __lt__(self, rhs):
        return self.gacha_at < rhs.gacha_at

    def __eq__(self, rhs):
        return self.gacha_at == rhs.gacha_at and self.user_id == rhs.user_id and self.situation_id == rhs.situation_id

    def __hash__(self):
        return (str(self.gacha_at) + str(self.user_id * self.situation_id)).__hash__()

    def __str__(self):
        return str({
            'situation_id': self.situation_id,
            'gacha_name': self.gacha_name,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'gacha_at': self.gacha_at,
            'gacha_id': self.gacha_id
        })


class BilibiliDrawcardCrawler:

    SAVEFILE = os.path.join(globals.datapath, 'save.pickle')

    def __init__(self):
        self._data = self._load_data(self.SAVEFILE)
        self._refresh_data()

    def _refresh_data(self):
        self._data = {i for i in self._data if ((time.time() - (i.gacha_at // 1000)) < (30 * 24 * 3600))}

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
        out = set()
        try:
            with open(filename, 'rb') as f:
                out = pickle.load(f)
        except OSError:
            import sys
            sys.excepthook(*sys.exc_info())
        return out

    async def fetch_once(self):
        try:
            spider_data = await self._spider()
            if not spider_data:
                return 0
            l = len(spider_data - self._data)
            self._data |= spider_data
            self._refresh_data()
            self._save_data(self.SAVEFILE, self._data)
            return l
        except:
            import sys
            sys.excepthook(*sys.exc_info())

    async def _spider(self):
        rawdata = await self._request_page(1, 10000)
        data = rawdata['data']
        items = set([DrawCard_Item(x) for x in data])
        if len(items) == 0:
            return None
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

    def get_data_by_username(self, user):
        ret = list(filter(lambda i: user in i.user_name, self._data))
        ret.sort()
        return ret

    def get_data_by_uid(self, user):
        ret = list(filter(lambda i: user in i.user_id, self._data))
        ret.sort()
        return ret


drawcard_crawler = BilibiliDrawcardCrawler()
