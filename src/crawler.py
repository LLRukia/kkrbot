import os
import sys
import time
import random
import sqlite3
import json
import argparse

import requests

from utils import Logger
from crawler import CardDB, Crawler

WORKDIR = '/home/rukia/bot/src/'
LOGPATH = os.path.join(WORKDIR, 'crawler.log')
DATADIR = '/home/rukia/cq/data/'
DATABASE = '/home/rukia/bot/data/cards.db'

parser = argparse.ArgumentParser(description='crawler for Bestdori cards')
parser.add_argument('operation', type=str, help='init or update')

def init(crawler, db):
    db.create_table()
    all_data = crawler.request_json('all_cards')

    for cid, data in all_data.items():
        overall = {}
        if data['rarity'] < 3:
            for s in ['performance', 'technique', 'visual']:
                if data['stat'].get('episodes'):
                    overall[s] = data['stat'][str(data['levelLimit'])][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s]
                else:
                    overall[s] = data['stat'][str(data['levelLimit'])][s]
        else:
            for s in ['performance', 'technique', 'visual']:
                if data['stat'].get('episodes'):
                    overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s] + data['stat']['training'][s]
                else:
                    overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['training'][s]
        
        if crawler.request_data(int(cid)) == 0:
            time.sleep(random.uniform(4, 5))

        db.insert(
            int(cid), 
            data['prefix'][0] or data['prefix'][1] or data['prefix'][2] or data['prefix'][3],
            data['characterId'],
            (data['characterId'] - 1) // 5 + 1,
            data['rarity'],
            data['attribute'],
            data['skillId'],
            overall['performance'],
            overall['technique'],
            overall['visual'],
            data['type'],
            data['resourceSetName']
        )

def update(crawler, db):
    local_all_cards = set([str(r[0]) for r in db.select('id')])
    all_data = crawler.request_json('all_cards')
    all_cards = set(all_data.keys())

    for cid in all_cards - local_all_cards:
        data = all_data[cid]
        overall = {}
        if data['rarity'] < 3:
            for s in ['performance', 'technique', 'visual']:
                if data['stat'].get('episodes'):
                    overall[s] = data['stat'][str(data['levelLimit'])][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s]
                else:
                    overall[s] = data['stat'][str(data['levelLimit'])][s]
        else:
            for s in ['performance', 'technique', 'visual']:
                if data['stat'].get('episodes'):
                    overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['episodes'][0][s] + data['stat']['episodes'][1][s] + data['stat']['training'][s]
                else:
                    overall[s] = data['stat'][str(data['levelLimit'] + 10)][s] + data['stat']['training'][s]
        
        if crawler.request_data(int(cid)) == 0:
            time.sleep(random.uniform(4, 5))

        db.insert(
            int(cid), 
            data['prefix'][0] or data['prefix'][1] or data['prefix'][2] or data['prefix'][3],
            data['characterId'],
            (data['characterId'] - 1) // 5 + 1,
            data['rarity'],
            data['attribute'],
            data['skillId'],
            overall['performance'],
            overall['technique'],
            overall['visual'],
            data['type'],
            data['resourceSetName']
        )

if __name__ == '__main__':
    args = parser.parse_args()
    assert args.operation in ['init', 'update']
    
    crawler = Crawler(
        Logger('crawler', LOGPATH),
        '/home/rukia/bot/data/json', os.path.join(DATADIR, 'image', 'assets')
    )
    db = CardDB(sqlite3.connect(DATABASE))
    
    getattr(sys.modules[__name__], args.operation)(crawler, db)