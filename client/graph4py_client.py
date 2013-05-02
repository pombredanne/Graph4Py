import ast
import _ast
import inspect

from multiprocessing.connection import Client


class Graph4PyClient(object):

    def __init__(self, host, port, authkey=None):
        self.address = (host, port)
        self.authkey = authkey

    def process(self, query, *args, **kwargs):
        connection = Client(self.address, authkey=self.authkey)
        name = query.func_name
        kwargs['name'] = name
        tree = ast.parse(inspect.getsource(query))
        tree = _ast.Module(tree.body[0].body)
        connection.send([tree, args, kwargs])
        result = connection.recv()
        connection.close()
        if result['type'] == 'result':
            return result['data']
        else:
            raise Exception(result['data'])
