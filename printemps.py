#!/usr/bin/env python
import sys
import time
import signal
import argparse
import traceback

from multiprocessing.connection import Listener


from blueprints import Graph
from setproctitle import setproctitle


__version__ = '0.1'


class Printemps(object):

    def __init__(self, backend, path, authkey):
        self.authkey = authkey
        self.graph = Graph(backend, path)
        self.running = True

    def process(self, connection):
        while self.running:
            while self.running:
                try:
                    tree, kwargs = connection.recv()
                except EOFError:
                    break
                else:
                    code = compile(tree, '<string>', 'exec')
                    result = dict()
                    kwargs['graph'] = self.graph
                    kwargs['result'] = result
                    locals().update(kwargs)
                    try:
                        exec code
                    except Exception, e:
                        message = '%s\n%s' % (e.message, kwargs)
                        message = '%s\n%s' % (message, traceback.format_exc())
                        connection.send({
                            'type': 'exception',
                            'data': message,
                        })
                    else:
                        connection.send({'type': 'result', 'data': result})

    def close(self):
        self.running = False
        time.sleep(1)
        self.graph.close()


def main():
    setproctitle('printemps')
    parser = argparse.ArgumentParser(description='Run Printemps graph server')
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=__version__
    )
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('backend')
    parser.add_argument('path')
    parser.add_argument('--authkey', '-k', action='store')
    args = parser.parse_args()

    database = Printemps(args.backend, args.path, args.authkey)

    def signal_handler(s, frame):
        database.close()
        time.sleep(1)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    listener = Listener((args.host, args.port), family='AF_INET')
    print 'Running on %s:%s' % (args.host, args.port)

    while True:
        connection = listener.accept()
        database.process(connection)
