
import os
import argparse
from aiocqhttp import CQHttp
import asyncio


def create_bot(server, bot_name='Common'):
    bot = None
    m = __import__(bot_name + 'Bot', fromlist=[''])
    for i in dir(m):
        bot_type = getattr(m, i)
        if isinstance(bot_type, type) and bot_type.__name__ == bot_name + 'Bot':
            bot = bot_type(server)
    return bot


def main():
    import sys
    cur_dir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append(os.path.realpath(os.path.join(cur_dir, 'lib')))
    sys.path.append(cur_dir)

    import logging
    from quart.logging import default_handler
    import const
    const.workpath = os.path.join(cur_dir, '..')
    const.cachepath = os.path.join(const.workpath, 'cache')
    const.datapath = os.path.join(const.workpath, 'data')
    const.user_profile_path = os.path.join(const.datapath, 'user_profile')
    const.asset_card_path = os.path.join(const.datapath, 'image', 'assets', 'cards')
    const.asset_card_thumb_path = os.path.join(const.datapath, 'image', 'assets', 'cards', 'thumb')
    const.asset_event_path = os.path.join(const.datapath, 'image', 'assets', 'events')
    const.asset_gacha_path = os.path.join(const.datapath, 'image', 'assets', 'gachas')
    const.asset_resource_path = os.path.join(const.datapath, 'image', 'assets', 'res')

    if not os.path.exists(const.user_profile_path):
        os.makedirs(const.user_profile_path)
    if not os.path.exists(const.asset_card_path):
        os.makedirs(const.asset_card_path)
    if not os.path.exists(const.asset_card_thumb_path):
        os.makedirs(const.asset_card_thumb_path)
    if not os.path.exists(const.asset_gacha_path):
        os.makedirs(const.asset_gacha_path)
    if not os.path.exists(const.asset_resource_path):
        os.makedirs(const.asset_resource_path)

    logger_handler = logging.FileHandler(os.path.realpath(os.path.join(const.workpath, 'log/app.log')))
    logger_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))

    cq_server = CQHttp(enable_http_post=False)
    cq_server.logger.removeHandler(default_handler)
    cq_server.logger.addHandler(logger_handler)
    cq_server.logger.setLevel(logging.INFO)
    cq_server.logger.info('begin create bot')
    if not os.path.exists(const.datapath):
        cq_server.logger.warn(f'running without data')
        os.mkdir(const.datapath)

    def handle_trace(*exc_info):
        def on_trace_back(type, value, tb):
            import linecache
            stacks = []
            localvars = []
            try:
                while tb:
                    f = tb.tb_frame
                    c = f.f_code
                    linecache.checkcache(c.co_filename)
                    line = linecache.getline(c.co_filename, f.f_lineno, f.f_globals)
                    stacks.append('File "%s", in %s\n > %d: %s' % (c.co_filename, c.co_name, f.f_lineno, line.strip() if line else "N/A"))
                    f.f_locals.pop("__builtins__", None)
                    localvars.append('\n'.join((("\t%19s : %s" % (n, repr(v)[:128])) for n, v in f.f_locals.items())))
                    tb = tb.tb_next
            except Exception as e:
                stacks.append(str(e))

            stacks.append("%s" % type.__name__)
            localvars.append(" > %s" % str(value))

            trace = "\n".join(("%s\n%s" % (s, l) for s, l in zip(stacks, localvars)))
            return trace

        cq_server.logger.error("Unhandled exception: %s", on_trace_back(*exc_info))

    sys.excepthook = handle_trace

    bot = create_bot(cq_server)
    if not bot:
        return
    import socket
    ip_address = socket.gethostbyname(socket.gethostname())
    cq_server.logger.info('bot created, bind success %s', bot.__class__.__name__)
    cq_server.run(host=ip_address, port=8080, debug=False)


if __name__ == '__main__':
    main()
