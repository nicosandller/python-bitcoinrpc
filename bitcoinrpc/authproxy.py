
"""
  Copyright 2011 Jeff Garzik

  AuthServiceProxy has the following improvements over python-jsonrpc's
  ServiceProxy class:

  - HTTP connections persist for the life of the AuthServiceProxy object
    (if server supports HTTP/1.1)
  - sends protocol 'version', per JSON-RPC 1.1
  - sends proper, incrementing 'id'
  - sends Basic HTTP authentication headers
  - parses all JSON numbers that look like floats as Decimal
  - uses standard Python json lib

  Previous copyright, from python-jsonrpc/jsonrpc/proxy.py:

  Copyright (c) 2007 Jan-Klaas Kollhof

  This file is part of jsonrpc.

  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

# try:
#     import http.client as httplib
# except ImportError:
#     import httplib
import requests
import json
from base64 import b64encode
# import base64
import decimal
import logging
# try:
#     import urllib.parse as urlparse
# except ImportError:
#     import urlparse

USER_AGENT = "AuthServiceProxy/0.1"

# HTTP_TIMEOUT = 30

log = logging.getLogger("BitcoinRPC")

# class JSONRPCException(Exception):
#     def __init__(self, rpc_error):
#         parent_args = []
#         try:
#             parent_args.append(rpc_error['message'])
#         except:
#             pass
#         Exception.__init__(self, *parent_args)
#         self.error = rpc_error
#         self.code = rpc_error['code'] if 'code' in rpc_error else None
#         self.message = rpc_error['message'] if 'message' in rpc_error else None
#
#     def __str__(self):
#         return '%d: %s' % (self.code, self.message)
#
#     def __repr__(self):
#         return '<%s \'%s\'>' % (self.__class__.__name__, self)
#
#

class AuthServiceProxy(object):
    __id_count = 0

    def __init__(self,
                 rpcuser,
                 rpcpasswd,
                 rpchost,
                 rpcport,
                 rpc_call=None,
                #  service_url,
                #  service_name=None,
                #  timeout=HTTP_TIMEOUT,
                #  connection=None
                 ):

        self.__rpcuser = rpcuser.encode('utf-8')
        self.__rpcpasswd = rpcpasswd.encode('utf-8')
        self.__rpchost = rpchost
        self.__rpcport = rpcport
        # self.__service_url = service_url
        self.__rpc_call = rpc_call
        # self.__service_name = service_name
        # self.__url = urlparse.urlparse(service_url)
        # if self.__url.port is None:
        #     port = 80
        # else:
        #     port = self.__url.port
        # (user, passwd) = (self.__url.username, self.__url.password)
        # try:
        #     user = user.encode('utf8')
        # except AttributeError:
        #     pass
        # try:
        #     passwd = passwd.encode('utf8')
        # except AttributeError:
        #     pass
        self.__auth_header = ' '.join(
            ['Basic', b64encode(':'.join([self.__rpcuser, self.__rpcpasswd]))]
        )
        self.__headers = {'Host': self.__rpchost,
                          'User-Agent': 'Savoir v0.1',
                          'Authorization': self.__auth_header,
                          'Content-type': 'application/json'
                          }
        # authpair = user + b':' + passwd
        # self.__auth_header = b'Basic ' + base64.b64encode(authpair)

        # self.__timeout = timeout
        # if connection:
        #     # Callables re-use the connection of the original proxy
        #     self.__conn = connection
        # elif self.__url.scheme == 'https':
        #     self.__conn = httplib.HTTPSConnection(self.__url.hostname, port,
        #                                           timeout=timeout)
        # else:
        #     self.__conn = httplib.HTTPConnection(self.__url.hostname, port,
        #                                          timeout=timeout)

    def __getattr__(self, name):
        """
        Return an instance of AuthServiceProxy with an rpc_call defined.
        When the attribute (method) is not defined (i.e: instance.getinfo()),
        then __getattr__ is called with the name (getinfo) as parameter.
        It then calls AuthServiceProxy as a function,
        defining self.rpc_call to the attribute's name.
        """
        print 'aparecio __getattr__:'
        print name
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        # If there is an rpc_call
        if self.__rpc_call is not None:
            name = "%s.%s" % (self.__rpc_call, name)
        # return AuthServiceProxy(self.__service_url, name, self.__timeout, self.__conn)
        return AuthServiceProxy(self.__rpcuser, self.__rpcpasswd,
                                self.__rpchost,
                                self.__rpcport,
                                name)

    def __call__(self, *args):
        print 'aparecio __call__'
        print args
        AuthServiceProxy.__id_count += 1

        # log.debug("-%s-> %s %s" % (AuthServiceProxy.__id_count, self.__service_name,
        #                          json.dumps(args, default=EncodeDecimal)))
        postdata = json.dumps({'version': '1.1',
                               'method': self.__rpc_call,
                               'params': args,
                               'id': AuthServiceProxy.__id_count}, default=self.EncodeDecimal)
        print 'postdata'
        print postdata
        # self.__conn.request('POST', self.__url.path, postdata,
        #                     {'Host': self.__url.hostname,
        #                      'User-Agent': USER_AGENT,
        #                      'Authorization': self.__auth_header,
        #                      'Content-type': 'application/json'})
        # self.__conn.sock.settimeout(self.__timeout)
        url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
        print url
        r = requests.post(url, data=postdata, headers=self.__headers)
        # response = self._get_response()
        if r.status_code == 200:
            log.info("Response: %s" % r.json())
            return r.json()['result']
        else:
            log.error("Error! Status code: %s" % r.status_code)
            log.error("Text: %s" % r.text)
            log.error("Json: %s" % r.json())
            return r.json()

        # if 'error' in response:
        #     if response['error'] is not None:
        #         raise JSONRPCException(response['error'])
        # elif 'result' not in response:
        #     raise JSONRPCException({
        #         'code': -343, 'message': 'missing JSON-RPC result'})
        #
        # return response['result']

    def batch_(self, rpc_calls):
        """Batch RPC call.
           Pass array of arrays: [ [ "method", params... ], ... ]
           Returns array of results.
        """
        batch_data = []
        for rpc_call in rpc_calls:
            AuthServiceProxy.__id_count += 1
            m = rpc_call.pop(0)
            batch_data.append({"jsonrpc":"2.0", "method":m, "params":rpc_call, "id":AuthServiceProxy.__id_count})

        postdata = json.dumps(batch_data, default=EncodeDecimal)
        log.debug("--> "+postdata)
        self.__conn.request('POST', self.__url.path, postdata,
                            {'Host': self.__url.hostname,
                             'User-Agent': USER_AGENT,
                             'Authorization': self.__auth_header,
                             'Content-type': 'application/json'})
        results = []
        responses = self._get_response()
        for response in responses:
            if response['error'] is not None:
                raise JSONRPCException(response['error'])
            elif 'result' not in response:
                raise JSONRPCException({
                    'code': -343, 'message': 'missing JSON-RPC result'})
            else:
                results.append(response['result'])
        return results

    def EncodeDecimal(o):
        if isinstance(o, decimal.Decimal):
            return float(round(o, 8))
        raise TypeError(repr(o) + " is not JSON serializable")

    # def _get_response(self):
    #     http_response = self.__conn.getresponse()
    #     if http_response is None:
    #         raise JSONRPCException({
    #             'code': -342, 'message': 'missing HTTP response from server'})
    #
    #     responsedata = http_response.read().decode('utf8')
    #     response = json.loads(responsedata, parse_float=decimal.Decimal)
    #     if "error" in response and response["error"] is None:
    #         log.debug("<-%s- %s"%(response["id"], json.dumps(response["result"], default=EncodeDecimal)))
    #     else:
    #         log.debug("<-- "+responsedata)
    #     return response
