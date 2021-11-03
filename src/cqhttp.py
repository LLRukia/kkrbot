
import os
import argparse
from aiocqhttp import CQHttp
import asyncio

parser = argparse.ArgumentParser(description='cqbot')
parser.add_argument('-d', '--datapath', type=str, help='static resource path',
                    nargs='*', default=os.path.abspath('./cq/data/'))


def create_bot(server, bot_type='Common'):
    bot = None
    m = __import__(bot_type + 'Bot', fromlist=[''])
    for n in dir(m):
        a = getattr(m, n)
        if isinstance(a, type) and a.__name__ == bot_type + 'Bot':
            bot = a(server)
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
    const.user_profile_path = os.path.join(
        const.workpath, 'data', 'user_profile')
    const.datapath = args.datapath
    const.asset_card_path = os.path.join(
        const.datapath, 'image', 'assets', 'cards')
    const.asset_card_thumb_path = os.path.join(
        const.datapath, 'image', 'assets', 'cards', 'thumb')
    const.asset_event_path = os.path.join(
        const.datapath, 'image', 'assets', 'events')
    const.asset_gacha_path = os.path.join(
        const.datapath, 'image', 'assets', 'gachas')
    const.asset_resource_path = os.path.join(
        const.datapath, 'image', 'assets', 'res')

    if not os.path.exists(const.user_profile_path):
        os.makedirs(
            const.user_profile_path)
    if not os.path.exists(const.asset_card_path):
        os.makedirs(
            const.asset_card_path)
    if not os.path.exists(const.asset_card_thumb_path):
        os.makedirs(
            const.asset_card_thumb_path)
    if not os.path.exists(const.asset_gacha_path):
        os.makedirs(
            const.asset_gacha_path)
    if not os.path.exists(const.asset_resource_path):
        os.makedirs(
            const.asset_resource_path)

    logger_handler = logging.FileHandler(os.path.realpath(
        os.path.join(const.workpath, 'log/app.log')))
    logger_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))

    cq_server = CQHttp(enable_http_post=False)
    cq_server.logger.removeHandler(default_handler)
    cq_server.logger.addHandler(logger_handler)
    cq_server.logger.setLevel(logging.INFO)
    cq_server.logger.info(f'datapath = {const.datapath}')
    cq_server.logger.info('begin create bot')

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
                    line = linecache.getline(
                        c.co_filename, f.f_lineno, f.f_globals)
                    stacks.append('File "%s", in %s\n > %d: %s' % (
                        c.co_filename, c.co_name, f.f_lineno, line.strip() if line else "N/A"))
                    f.f_locals.pop("__builtins__", None)
                    localvars.append('\n'.join(
                        (("\t%19s : %s" % (n, repr(v)[:128])) for n, v in f.f_locals.iteritems())))
                    tb = tb.tb_next
            except Exception as e:
                stacks.append(str(e))

            stacks.append("%s" % type.__name__)
            localvars.append(" > %s" % str(value))

            trace = "\n".join(("%s\n%s" % (s, l)
                              for s, l in zip(stacks, localvars)))
            return trace

        cq_server.logging.error("Unhandled exception: %s", on_trace_back(*exc_info))

    sys.excepthook = handle_trace

    bot = create_bot(cq_server)
    if not bot:
        return
    import socket
    ip_address = socket.gethostbyname(socket.gethostname())
    cq_server.logger.info('bot created, bind success %s',
                          bot.__class__.__name__)
    cq_server.run(host=ip_address, port=8080, debug=False)


if __name__ == '__main__':
    main()
