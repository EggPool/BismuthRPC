#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test and dev json-rpc client 
"""

import time

# http://jsonrpcclient.readthedocs.io/en/latest/api.html
import jsonrpcclient
from jsonrpcclient.http_client import HTTPClient

jsonrpcclient.config.validate = False

# The test bismuthd.py server
client = HTTPClient('http://username:password@127.0.0.1:8115/')



## AUTH ##

# Simple Auth - see http://docs.python-requests.org/en/master/user/authentication/
client.session.auth = ('username', 'password')

## Misc ##
client.session.headers.update({'Connection': 'close'})


## Requests ##

client.request('getinfo')

# New functions
client.request('getdifficulty')
client.request('getblockhash', 10000)
client.request('getrawmempool')


