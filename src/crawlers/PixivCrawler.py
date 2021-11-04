import json
import logging
import os
import random
import shutil
from collections import defaultdict

from pixivpy3 import PixivAPI

import pymongo

_logger = logging.getLogger('quart.app')


class PixivCursor:
    MODES = ['daily', 'male', 'female', 'daily_r18']
    MONGO_DB = pymongo.MongoClient("mongodb://localhost:27017/")['pixiv']
    ILLUSTS = MONGO_DB['illusts']

    @staticmethod
    def init():
        i = pymongo.IndexModel([('work_id', pymongo.ASCENDING)], name='iid')
        u = pymongo.IndexModel([('used', pymongo.ASCENDING)], name='u')
        uu = pymongo.IndexModel([('used', pymongo.ASCENDING), ('user', pymongo.DESCENDING)], name='uu')
        um = pymongo.IndexModel([('used', pymongo.ASCENDING), ('mode', pymongo.DESCENDING)], name='um')
        umu = pymongo.IndexModel([('used', pymongo.ASCENDING), ('mode', pymongo.DESCENDING), ('user', pymongo.DESCENDING)], name='umu')
        PixivCursor.ILLUSTS.create_indexes([i, u, uu, um, umu])

    @staticmethod
    def insert_update_one(meta):
        meta.update({'used': []})
        if PixivCursor.ILLUSTS.find_one({'work_id': meta['work_id']}):
            PixivCursor.ILLUSTS.update_one({'work_id': meta['work_id']}, {'$set': meta})
        else:
            PixivCursor.ILLUSTS.insert_one(meta)

    @staticmethod
    def get_one(query={}, dirty_flag=None):
        if dirty_flag is None:
            query.update({'used': {'$ne': dirty_flag}})
        else:
            query.update({'used': {'$size': 0}})
        ret = PixivCursor.ILLUSTS.find_one(query)
        if ret:
            PixivCursor.ILLUSTS.update_one({'_id': ret['_id']}, {'$push': {'used': dirty_flag}})
            return ret['fn'], json.loads(ret['meta'])


class PixivCrawler:
    KKRTAG = ['弦巻こころ']

    def __init__(self, auth, work_path=os.path.abspath('../pixiv/'), ):
        self._api = PixivAPI()
        self._api.login(*auth)
        self._wd = work_path

    def fetch_work(self, work_id, tag):
        got = False
        ri = self._api.works(work_id)
        try:
            r = ri.response[0]
        except:
            r = None
        if not r:
            return got
        url_list = []
        if r.metadata:
            for p in r.metadata.pages:
                url_list.append(p.image_urls.large)
        else:
            url_list.append(r.image_urls.large)

        created_time = r.created_time[:10].replace('-', '')
        wd = os.path.join(self._wd, created_time)
        if not os.path.isdir(wd):
            os.mkdir(wd)
        fns = []

        for url in url_list:
            fn = os.path.basename(url)
            final_fn = os.path.join(created_time, fn)
            _logger.info('getting %s to %s', url, wd)
            try:
                if self._api.download(url, fname=fn, path=wd):
                    got = True
                    shutil.move(os.path.join(wd, fn), os.path.join(wd, fn + '.download'))
                fns.append(final_fn)
            except:
                import sys
                sys.excepthook(*sys.exc_info())
        if fns:
            meta = json.dumps(r)
            dmeta = {
                'work_id': work_id,
                'mode': tag,
                'user': r.user.id,
                'fn': fns,
                'meta': meta,
            }
            PixivCursor.insert_update_one(dmeta)
        return got

    def get_by_tag(self, search_tag='', filter_tag=[], num=30, save_tag=''):
        if not search_tag and not filter_tag:
            return None
        if filter_tag:
            filter_tag = [x.strip().lower() for x in filter_tag]
        if not search_tag:
            search_tag = filter_tag[0]
            filter_tag = filter_tag[1:]
        if not save_tag:
            save_tag = search_tag
        filter_tag = set(filter_tag)
        _logger.info('search: %s filter: %s', search_tag, filter_tag)
        ret = 0
        page = 1
        while ret < num:
            r = self._api.search_works(search_tag, mode='tag', page=page, per_page=30)
            try:
                l = r.response
            except:
                l = None

            if not l:
                break
            _logger.info('get %d illusts', len(l))
            for i in l:
                if i.type != 'illustration':
                    continue
                tt = set([x.strip().lower() for x in i.tags])
                if len(tt & filter_tag) != len(filter_tag):
                    continue
                if self.fetch_work(i.id, save_tag):
                    ret += 1
                if ret > num:
                    break
            page += 1

        return ret

    def get_rank(self, mode='daily', num=30):
        ret = 0
        page = 1
        while ret < num:
            r = self._api.ranking_all(mode=mode, page=page, per_page=30)
            try:
                l = r.response[0].works
            except:
                l = None
            if not l:
                break
            _logger.info('get %d ranking illust', len(l))
            for i in l:
                if i.work.type != 'illustration':
                    continue
                if self.fetch_work(i.work.id, mode):
                    ret += 1
                if ret >= num:
                    break
            page += 1
        return ret


if __name__ == '__main__':
    # usage
    # python3 pixiv_crawler.py -m all -u balabala -p palapala -d /path/to/pixiv/
    # python3 pixiv_crawler.py -u balabala -p palapala -d /path/to/pixiv/ -n 30 --savetag kkr -s 弦巻こころ
    import argparse
    parser = argparse.ArgumentParser(description='crawler for Pixiv')
    parser.add_argument('--init', type=bool, help='init db', default=False)
    parser.add_argument('-u', '--username', type=str, help='username')
    parser.add_argument('-p', '--password', type=str, help='password')
    parser.add_argument('-m', '--mode', type=str, help='mode (Past): [all, daily, weekly, monthly, male, female, original,\
        rookie, daily_r18, weekly_r18, male_r18, female_r18, r18g]')
    parser.add_argument('-d', '--datapath', type=str, help='path to download', default=os.path.abspath('../pixiv/'))
    parser.add_argument('-n', '--num', type=int, help='how much', default=30)
    parser.add_argument('-s', '--search', type=str, nargs='*', help='tags to search', default=30)
    parser.add_argument('--savetag', type=str, help='tags to save', default=30)
    args = parser.parse_args()
    _logger.setLevel(logging.INFO)
    import sys
    _logger.addHandler(logging.StreamHandler(sys.stdout))
    if args.init:
        PixivCursor.init()
    pc = PixivCrawler((args.username, args.password), args.datapath)
    if args.mode == 'all':
        for x in PixivCursor.MODES:
            _logger.info(pc.get_rank(x, args.num))
    elif args.mode:
        _logger.info(pc.get_rank(args.mode, args.num))
    elif args.search:
        _logger.info(pc.get_by_tag(filter_tag=args.search, num=args.num, save_tag=args.savetag))
