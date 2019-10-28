import functools
import time
import requests
import pickle
import os

class RollbackError(Exception):
    def __init__(self, new, old):
        self.new = new
        self.old = old

    def __str__(self):
        return 'Data rollback: new {} = old {}'.format(self.new, self.old)

class Bilibili_DrawCard_Spider:

    SAVEFILE = 'save.pickle'

    def __init__(self):
        self._data = self._load_data(self.SAVEFILE)

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
        out = []
        try:
            with open(filename, 'rb') as f:
                out = pickle.load(f)
        except OSError:
            import traceback
            traceback.print_exc()
        return out

    def fetch_once(self):
        try:
            lastitems = self._data[-10000:] if self._data else None
            new_data = self._spider(lastitems)
            if len(new_data) > 100:
                pass
            print('append {} items'.format(len(new_data)))
            self._data.extend(new_data)
            self._save_data(self.SAVEFILE, self._data)
        except RollbackError as e:
            print(e)
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _spider(self, lastitems=None):
        rawdata = self._request_page(1, 10000)
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

    @functools.lru_cache()
    def _fetch_json_from_bestdori(self, url):
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_gacha_name(self, gacha):
        d = self._fetch_json_from_bestdori('https://bestdori.com/api/gacha/all.5.json')
        namelist = d[str(gacha)]['gachaName']
        return self._locale(namelist, 3)

    @staticmethod
    def _locale(l, lang, default=''):
        if lang < len(l) and l[lang]:
            return l[lang]
        for name in l:
            if name: return name
        return default