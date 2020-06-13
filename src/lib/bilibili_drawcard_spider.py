import functools
import os
import pickle
import time

import requests

import const


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

class Bilibili_DrawCard_Spider:

    SAVEFILE = os.path.join(const.workpath, 'cache/save.pickle')

    def __init__(self):
        self._data = self._load_data(self.SAVEFILE)
        self._refresh_data()

    def _refresh_data(self):
        self._data = {i for i in self._data if ((time.time() - (i.gacha_at // 1000)) < (30 * 24* 3600))}

    def _save_data(self, filename, data):
        try:
            tempname = filename + '.tmp'
            with open(tempname, 'wb') as f:
                pickle.dump(data, f)
            os.replace(tempname, filename)
        except OSError:
            import traceback
            traceback.print_exc()

    def _load_data(self, filename):
        out = set()
        try:
            with open(filename, 'rb') as f:
                out = pickle.load(f)
        except OSError:
            import traceback
            traceback.print_exc()
        return out

    def fetch_once(self):
        try:
            spider_data = self._spider()
            print('append {} items'.format(len(spider_data)))
            if not spider_data:
                return 0
            l = len(spider_data - self._data)
            self._data |= spider_data
            self._refresh_data()
            self._save_data(self.SAVEFILE, self._data)
            return l
        except:
            import traceback
            traceback.print_exc()

    def _spider(self):
        rawdata = self._request_page(1, 10000)
        data = rawdata['data']
        items = set([DrawCard_Item(x) for x in data])
        if len(items) == 0:
            return None
        return items

    def _request_page(self, page=1, limit=20):
        payload = {
            'page': page,
            'limit': limit,
            '_': int(time.time() * 1000)
        }
        r = requests.get('https://qcloud-sdkact-api.biligame.com/bangdream/h5/user/situation/all', payload, timeout=20)
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

if __name__ == '__main__':
    Bilibili_DrawCard_Spider.SAVEFILE = '/home/rukia/bot/cache/save.pickle'
    b = Bilibili_DrawCard_Spider()
    for i in b._data:
        print(i.gacha_at)
        break
