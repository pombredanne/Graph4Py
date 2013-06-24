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


class ObjectsGraph(Graph):

    def create_vertex_object(self, mro):
        vertex = self.create_vertex()
        index = self.__get_or_create_index('objects', Graph.VERTEX)
        for class_name in mro:
            index.put('vertices', class_name, vertex)
        return vertex

    def __get_or_create_index(self, name, klass):
        index = self.index.get('objects', klass)
        if not index:
            index = self.index.create('objects', klass)
        return index

    def create_edge_object(self, start, label, end, mro):
        edge = self.create_edge(start, label, end)
        index = self.__get_or_create_index('objects', Graph.EDGE)
        for class_name in mro:
            index.put('edges', class_name, edge)
        return edge

    def iter_objects(self, class_name):
        index = self.__get_or_create_index('objects', Graph.VERTEX)
        if not index:
            index = self.__get_or_create_index('objects', Graph.EDGE)
            if not index:
                raise StopIteration
            else:
                return index.get('edges', class_name)
        else:
            return index.get('vertex', class_name)


class Graph4Py(object):

    def __init__(self, backend, path, authkey):
        self.authkey = authkey
        self.graph = ObjectsGraph(backend, path)

    def process(self, connection):
        self.running = True
        while self.running:
            try:
                tree, kwargs = connection.recv()
            except EOFError:
                continue
            else:
                result = dict()
                local = dict()
                local['graph'] = self.graph
                local['result'] = result
                local['values'] = kwargs
                try:
                    code = compile(tree, '<string>', 'exec')
                    exec code in local
                except Exception, e:
                    message = '%s\n\n%s\n\n' % (e.message, kwargs)
                    message = '%s%s' % (message, traceback.format_exc())
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
    setproctitle('graph4py')
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
    args = parser.parse_args()

    database = Graph4Py(args.backend, args.path, args.authkey)

    def signal_handler(s, frame):
        database.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    listener = Listener((args.host, args.port), family='AF_INET')
    print 'Running on %s:%s' % (args.host, args.port)

    while True:
        connection = listener.accept()
        database.process(connection)


if __name__ == '__main__':
    main()
