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
import PimOps
from multiprocessing import TimeoutError

class ListResDetails(object):
    '''
    List resource(pimCm), alarm(pimFm), metrics(pimPm) class, proxy to PIM backend with process pool     
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
    res = Response()
    # check keystone token first
    v = PimOps.checkToken(req.environ['HTTP_X_AUTH_TOKEN'])
    if not v :
        #fail to check token, return directly
        res.status = 401
        content = []
        content.append("Relay Request Error:UNAUTHORIZED")
        res.body = '\n'.join(content) 
        return res
    # relay the NFVO request to PIM backend which identified by pimIP
    c = httplib.HTTPConnection(host=pimIP,timeout=1)
    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": req.environ['HTTP_X_AUTH_TOKEN']}
    try:
        c.request(req.method, req.script_name+"?"+req.query_string, None, headers)
        pimres = c.getresponse()
        res.status = pimres.status
        res.body = pimres.read()
        #PIM connection is OK, but API failed
        checkPimResStatus(pimres)
    except Exception, exc:
        log.error("Check network connection between PIM and PIM plugin!!!")
        log.exception('Req header is %s,Req script_name is %s,Req query_string is %s'\
                   %(req.headers.items(),req.script_name,req.query_string))
        print ('Req header is %s,Req script_name is %s,Req query_string is %s'\
                   %(req.headers.items(),req.script_name,req.query_string))
        res.status = 500
        content = []
        content.append("Relay Request Error: failed to get response from PIM")
        res.body = '\n'.join(content)
    return res

def checkPimResStatus(res):
    # check PIM response status, write log if error
    if ( 200<= res.status <300):
        print ("List Resource Success,Return Code(%s)"%res.status)
        log.debug("List Resource Success,Return Code(%s)"%res.status)
    else:
        print ("List resource PIM-SIDE Failed, PIM return Wrong Code(%s)" %res.status)
        log.error("List resource PIM-SIDE Failed, PIM return Wrong Code(%s)" %res.status)


