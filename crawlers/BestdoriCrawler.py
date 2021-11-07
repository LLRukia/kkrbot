import os
import argparse

from utils.logger import Logger
from bestdori import CardTable, CardCrawler, EventTable, EventCrawler, GachaTable, GachaCrawler, resource_map
from bestdori.connection import event_gacha

parser = argparse.ArgumentParser(description='crawler for Bestdori assets')
parser.add_argument('operation', type=str, help='init or update')
parser.add_argument('-c', '--content', type=str, help='card, event or gacha', nargs='*')
parser.add_argument('-d', '--datapath', type=str, help='static resource path', default=os.path.abspath('../data'))

if __name__ == '__main__':
    args = parser.parse_args()
    work_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(work_dir, 'crawler.log')
    asset_dir = os.path.join(args.datapath, 'image/assets/')
    json_dir = os.path.join(args.datapath, 'json')
    db_file = os.path.join(args.datapath, 'bestdori.db')

    logger = Logger('crawler', log_file)

    card_crawler = CardCrawler(
        logger, CardTable(db_file), {
            'overall_json': json_dir,
            'json': os.path.join(json_dir, 'cards'),
            'assets': os.path.join(asset_dir, 'cards'),
        }, 'https://bestdori.com/api/cards/'
    )

    event_crawler = EventCrawler(
        logger, EventTable(db_file), {
            'overall_json': json_dir,
            'json': os.path.join(json_dir, 'events'),
            'assets': os.path.join(asset_dir, 'events'),
        }, 'https://bestdori.com/api/events/'
    )

    gacha_crawler = GachaCrawler(
        logger, GachaTable(db_file), {
            'overall_json': json_dir,
            'json': os.path.join(json_dir, 'gachas'),
            'assets': os.path.join(asset_dir, 'gachas'),
        }, 'https://bestdori.com/api/gacha/'
    )
    if args.operation in ['init', 'update']:
        content = set(args.content or ['card', 'event', 'gacha']) & set(['card', 'event', 'gacha'])
        for c in content:
            logger.info(f'eval ing {c}_crawler {args.operation}')
            getattr(eval(f'{c}_crawler'), args.operation)()
        if content >= set(['event', 'gacha']) or 'event-gacha' in args.content:
            event_gacha(
                json_dir,
                db_file,
                os.path.join(json_dir, 'event_gacha.json'),
                logger,
            )
