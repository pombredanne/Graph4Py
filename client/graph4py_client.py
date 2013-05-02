import ast
import _ast
import inspect

from multiprocessing.connection import Client

__version__ = '0.1'


class Graph4PyClient(object):

    def __init__(self, host, port, authkey=None):
        self.address = (host, port)
        self.authkey = authkey

    def process(self, query, **kwargs):
        connection = Client(self.address, authkey=self.authkey)
        name = query.func_name
        kwargs['name'] = name
        tree = ast.parse(inspect.getsource(query))
        tree = _ast.Module(tree.body[0].body)
        connection.send([tree, kwargs])
        result = connection.recv()
        connection.close()
        if result['type'] == 'result':
            return result['data']
        else:
            raise Exception(result['data'])
