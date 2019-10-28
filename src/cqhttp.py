
from aiocqhttp import CQHttp

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
    import sys
    import os
    filedir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(os.path.realpath(os.path.join(filedir, 'lib')))
    sys.path.append(filedir)
    
    import logging
    from quart.logging import default_handler
    import const
    const.workpath = os.path.join(filedir, '..')
    const.cachepath = os.path.join(const.workpath, 'cache')
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
