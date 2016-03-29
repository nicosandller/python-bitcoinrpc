import requests
import json
from base64 import b64encode
from requests.exceptions import ConnectionError
import logging

log = logging.getLogger("BitcoinRPC")


class AuthServiceProxy(object):
    __id_count = 0

    def __init__(self,
                 rpcuser,
                 rpcpasswd,
                 rpchost,
                 rpcport,
                 rpc_call=None,
                 ):

        self.__rpcuser = rpcuser.encode('utf-8')
        self.__rpcpasswd = rpcpasswd.encode('utf-8')
        self.__rpchost = rpchost
        self.__rpcport = rpcport
        self.__rpc_call = rpc_call
        self.__auth_header = ' '.join(
            ['Basic', b64encode(':'.join([self.__rpcuser, self.__rpcpasswd]))]
        )
        self.__headers = {'Host': self.__rpchost,
                          'User-Agent': 'Savoir v0.1',
                          'Authorization': self.__auth_header,
                          'Content-type': 'application/json'
                          }

    def __getattr__(self, name):
        """
        Return an instance of AuthServiceProxy with an rpc_call defined.
        When the attribute (method) is not defined (i.e: instance.getinfo()),
        then __getattr__ is called with the name (getinfo) as parameter.
        It then calls AuthServiceProxy as a function,
        defining self.rpc_call to the attribute's name.
        """
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__rpc_call is not None:
            name = "%s.%s" % (self.__rpc_call, name)
        # Return an instance of the client. Will call the __call__ method.
        return AuthServiceProxy(self.__rpcuser, self.__rpcpasswd,
                                self.__rpchost,
                                self.__rpcport,
                                name)

    def __call__(self, *args):
        AuthServiceProxy.__id_count += 1
        # log.debug("-%s-> %s %s" % (AuthServiceProxy.__id_count, self.__service_name,
        #                          json.dumps(args, default=EncodeDecimal)))
        postdata = json.dumps({'version': '1.1',
                               'method': self.__rpc_call,
                               'params': args,
                               'id': AuthServiceProxy.__id_count
                               },
                              default=self.EncodeDecimal
                              )
        url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
        try:
            r = requests.post(url, data=postdata, headers=self.__headers)
        except ConnectionError:
            print 'There was a problem connecting to the RPC daemon.'
            print 'Check the connection and connection parameters:'
            print 'Host: %s, Port: %s, Username: %s, Password: %s' \
                % (self.__rpchost, self.__rpcport, self.__rpcuser,
                   self.__rpcpasswd)
            return ConnectionError
        if r.status_code == 200:
            log.info("Response: %s" % r.json())
            return r.json()['result']
        else:
            log.error("Error! Status code: %s" % r.status_code)
            log.error("Text: %s" % r.text)
            log.error("Json: %s" % r.json())
            return r.json()

    # def batch_(self, rpc_calls):
    #     """Batch RPC call.
    #        Pass array of arrays: [ [ "method", params... ], ... ]
    #        Returns array of results.
    #     """
    #     batch_data = []
    #     for rpc_call in rpc_calls:
    #         AuthServiceProxy.__id_count += 1
    #         m = rpc_call.pop(0)
    #         batch_data.append({"jsonrpc":"2.0", "method":m, "params":rpc_call, "id":AuthServiceProxy.__id_count})
    #
    #     postdata = json.dumps(batch_data, default=EncodeDecimal)
    #     log.debug("--> "+postdata)
    #     self.__conn.request('POST', self.__url.path, postdata,
    #                         {'Host': self.__url.hostname,
    #                          'User-Agent': USER_AGENT,
    #                          'Authorization': self.__auth_header,
    #                          'Content-type': 'application/json'})
    #     results = []
    #     responses = self._get_response()
    #     for response in responses:
    #         if response['error'] is not None:
    #             raise JSONRPCException(response['error'])
    #         elif 'result' not in response:
    #             raise JSONRPCException({
    #                 'code': -343, 'message': 'missing JSON-RPC result'})
    #         else:
    #             results.append(response['result'])
    #     return results
    #
    # def EncodeDecimal(o):
    #     if isinstance(o, decimal.Decimal):
    #         return float(round(o, 8))
    #     raise TypeError(repr(o) + " is not JSON serializable")
