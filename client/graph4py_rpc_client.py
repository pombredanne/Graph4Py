from multiprocessing.connection import Client

__version__ = '0.2'


class Graph4PyRPCClient(object):

    def __init__(self, host, port, authkey=None):
        self.address = (host, port)
        self.authkey = authkey

    def __getattribute__(self, method_name):
        if method_name not in ['address', 'authkey']:
            address = self.address
            authkey = self.authkey

            def method(*args, **kwargs):
                connection = Client(address, authkey=authkey)
                connection.send([method_name, args, kwargs])
                result = connection.recv()
                connection.close()
                if result['type'] == 'result':
                    return result['data']
                else:
                    raise Exception(result['data'])
            return method
        else:
            return super(Graph4PyRPCClient, self).__getattribute__(method_name)
