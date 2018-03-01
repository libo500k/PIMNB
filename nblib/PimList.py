#!/user/bin/env python

"""
PimList.py
   : Operation class for NFV PIM northbound List functions
"""

__author__     = "Li Bo"
__copyright__  = "Copyright 2018, Lenovo Research"

import webob
import sys
import signal,time,threading
import pprint
import json
import MySQLdb
import PimAssist
import re
import copy
import pdb
import httplib, urllib
import socket
import ssl
import dateutil.parser
import datetime
import uuid


from webob import Response
from webob import Request
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
from OpenSSL import SSL
import PimLogger as log
import PimPool as pool
from multiprocessing import TimeoutError

class ListResDetails(object):
    '''
    List resource class, proxy to PIM backend with process pool     
    ''' 
    def __init__(self,a):
        return

    def __call__(self,environ,start_response):
        req = Request(environ)
        m = req.method
        if m == 'GET':
            # list resource handler for GET method
            # Response will be handled in process pool, 
            # no need to check return value 
            res = ListRes(req)
            return res(environ,start_response) 

def ListRes(req):
    pimIP = PimAssist.Config().getValue('PIM_IP')
    return RelayRequest(req,pimIP)

def RelayRequest(req,pimIP):
    print pimIP
    print "-------------------------------------------------"
    res = Response()
    return res

def checkResStatus(res1, res2):
    # check PIM response status, write log if error
    if ( 200<= res1 <300):
        print ("List Resource Success,Return Code(%s)"%res1)
        log.debug("List Resource Success,Return Code(%s)"%res1)
    else:
        print ("List resource PIM-SIDE Failed, PIM return Wrong Code(%s)" %res1)
        log.error("List resource PIM-SIDE Failed, PIM return Wrong Code(%s)" %res1)
    # check NFVO response status, write log if error
    if ( 200<= res2 <300):
        print ("List Resource Success,Return Code(%s)"%res2)
        log.debug("List Resource Success,Return Code(%s)"%res2)
    else:
        print ("List resource NFVO-SIDE Failed, NFVO return Wrong Code(%s)" %res2)
        log.error("List resource NFVO-SIDE Failed, NFVO return Wrong Code(%s)" %res2)


