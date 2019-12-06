
import os, argparse
from aiocqhttp import CQHttp

parser = argparse.ArgumentParser(description='cqbot')
parser.add_argument('-d', '--datapath', type=str, help='static resource path', nargs='*', default=os.path.abspath('../../cq/data/'))

def create_bot(server, bot_type='Common'):
    bot = None
    try:
        m = __import__(bot_type + 'Bot', fromlist=[''])
        for n in dir(m):
            a = getattr(m, n)
            if isinstance(a, type) and a.__name__ == bot_type + 'Bot':
                bot = a(server)
    except ImportError:
        server.logger.error('Cannot Import Bottype %s', bot_type)
    return bot

def main():
    args = parser.parse_args()
    
    import sys
    filedir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(os.path.realpath(os.path.join(filedir, 'lib')))
    sys.path.append(filedir)
    
    import logging
    from quart.logging import default_handler
    import const
    const.workpath = os.path.join(filedir, '..')
    const.cachepath = os.path.join(const.workpath, 'cache')
    const.user_profile_path = os.path.join(const.workpath, 'data', 'user_profile')
    const.datapath = args.datapath
    const.asset_card_path = os.path.join(const.datapath, 'image', 'assets', 'cards')
    const.asset_card_thumb_path = os.path.join(const.datapath, 'image', 'assets', 'cards', 'thumb')
    const.asset_event_path = os.path.join(const.datapath, 'image', 'assets', 'events')
    const.asset_gacha_path = os.path.join(const.datapath, 'image', 'assets', 'gachas')
    const.asset_resource_path = os.path.join(const.datapath, 'image', 'assets', 'res')
    
    if not os.path.exists(const.user_profile_path): os.makedirs(const.user_profile_path)
    if not os.path.exists(const.asset_card_path): os.makedirs(const.asset_card_path)
    if not os.path.exists(const.asset_card_thumb_path): os.makedirs(const.asset_card_thumb_path)
    if not os.path.exists(const.asset_gacha_path): os.makedirs(const.asset_gacha_path)
    if not os.path.exists(const.asset_resource_path): os.makedirs(const.asset_resource_path)
    
    logger_handler = logging.FileHandler(os.path.realpath(os.path.join(const.workpath, 'app.log')))
    logger_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    cq_server = CQHttp(enable_http_post=False)
    cq_server.logger.removeHandler(default_handler)
    cq_server.logger.addHandler(logger_handler)
    cq_server.logger.setLevel(logging.INFO)
    cq_server.logger.info('begin create bot')

    bot = create_bot(cq_server)
    if not bot:
        return
    import socket
    ip_address = socket.gethostbyname(socket.gethostname())
    cq_server.logger.info('bot created, bind success %s', bot.__class__.__name__)
    cq_server.run(host=ip_address, port=8080, debug=False)
    
if __name__ == '__main__':
    main()
