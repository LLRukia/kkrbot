import os
import argparse

from utils import Logger
from crawler import CardTable, CardCrawler, EventTable, EventCrawler, GachaTable, GachaCrawler

WORKDIR = os.path.dirname(os.path.abspath(__file__))
LOGPATH = os.path.join(WORKDIR, 'crawler.log')
DATADIR = os.path.join(os.path.dirname(WORKDIR), 'data')
ASSETDIR = '/home/rukia/cq/data/image/assets/'
# ASSETDIR = os.path.join(DATADIR, 'assets')
JSONDIR = os.path.join(DATADIR, 'json')
DATABASE = os.path.join(DATADIR, 'bestdori.db')

parser = argparse.ArgumentParser(description='crawler for Bestdori assets')
parser.add_argument('operation', type=str, help='init or update')
parser.add_argument('-c', '--content', type=str, help='card or event')

if __name__ == '__main__':
    args = parser.parse_args()
    assert args.operation in ['init', 'update']
    logger = Logger('crawler', LOGPATH)
    
    card_crawler = CardCrawler(
        logger, CardTable(DATABASE), {
            'overall_json': JSONDIR,
            'json': os.path.join(JSONDIR, 'cards'),
            'assets': os.path.join(ASSETDIR, 'cards'),
        }, 'https://bestdori.com/api/cards/'
    )
    
    event_crawler = EventCrawler(
        logger, EventTable(DATABASE), {
            'overall_json': JSONDIR,
            'json': os.path.join(JSONDIR, 'events'),
            'assets': os.path.join(ASSETDIR, 'events'),
        }, 'https://bestdori.com/api/events/'
    )

    gacha_crawler = GachaCrawler(
        logger, GachaTable(DATABASE), {
            'overall_json': JSONDIR,
            'json': os.path.join(JSONDIR, 'gachas'),
            'assets': os.path.join(ASSETDIR, 'gachas'),
        }, 'https://bestdori.com/api/gacha/'
    )

    getattr(eval(f'{args.content}_crawler'), args.operation)()
