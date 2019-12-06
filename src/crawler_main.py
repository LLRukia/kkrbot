import os
import argparse

from utils import Logger
from crawler import CardTable, CardCrawler, EventTable, EventCrawler, GachaTable, GachaCrawler
from crawler.connection import event_gacha

parser = argparse.ArgumentParser(description='crawler for Bestdori assets')
parser.add_argument('operation', type=str, help='init or update')
parser.add_argument('-c', '--content', type=str, help='card, event or gacha', nargs='*')
parser.add_argument('-d', '--datapath', type=str, help='static resource path', nargs='*', default=os.path.abspath('../../cq/data/'))

if __name__ == '__main__':
    args = parser.parse_args()
    WORKDIR = os.path.dirname(os.path.abspath(__file__))
    LOGPATH = os.path.join(WORKDIR, 'crawler.log')
    DATADIR = os.path.join(os.path.dirname(WORKDIR), 'data')
    ASSETDIR = args.datapath
    JSONDIR = os.path.join(DATADIR, 'json')
    DATABASE = os.path.join(DATADIR, 'bestdori.db')
    
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
    if args.operation in ['init', 'update']:
        content = set(args.content or ['card', 'event', 'gacha']) & set(['card', 'event', 'gacha'])
        for c in content:
            getattr(eval(f'{c}_crawler'), args.operation)()
        if content >= set(['event', 'gacha']) or 'event-gacha' in args.content:
            event_gacha(
                JSONDIR,
                DATABASE,
                os.path.join(JSONDIR, 'event_gacha.json'),
                logger,
            )
