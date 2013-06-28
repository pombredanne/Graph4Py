#!/usr/bin/env python
import sys
import time
import signal
import argparse
import traceback

from multiprocessing.connection import Listener

from setproctitle import setproctitle

from graph4py import ObjectsGraph


__version__ = '0.2'


def import_object(name):
    mod = __import__('.'.join(name.split('.')[:-1]))
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class Graph4Py(object):

    def __init__(self, backend, path, authkey, graph_class=None):
        if not graph_class:
            graph_class = ObjectsGraph
        self.authkey = authkey
        self.graph = graph_class(backend, path)

    def process(self, connection):
        try:
            method, args, kwargs = connection.recv()
        except EOFError:
            pass
        else:
            try:
                print 'exec'
                result = getattr(self.graph, method)(*args, **kwargs)
            except Exception, e:
                message = '%s\n\n%s\n\n' % (e.message, kwargs)
                message = '%s%s' % (message, traceback.format_exc())
                connection.send({
                    'type': 'exception',
                    'data': message,
                })
            else:
                print 'sending'
                connection.send({'type': 'result', 'data': result})

    def close(self):
        print 'closing'
        self.running = False
        time.sleep(1)
        self.graph.close()


def main():
    setproctitle('graph4py.rpc')
    parser = argparse.ArgumentParser(description='Run Graph4Py graph server')
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
    parser.add_argument('--graph', '-g', action='store')
    args = parser.parse_args()

    graph_class = import_object(args.graph) if args.graph else None

    database = Graph4Py(args.backend, args.path, args.authkey, graph_class)

    def signal_handler(s, frame):
        database.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    listener = Listener((args.host, args.port), family='AF_INET')
    print 'Running on %s:%s with %s' % (args.host, args.port, database.graph)

    while True:
        connection = listener.accept()
        database.process(connection)


if __name__ == '__main__':
    main()
