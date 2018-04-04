#!/user/bin/env python

"""
PimSet.py
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
import psycopg2
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
import base64

from webob import Response
from webob import Request
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
from OpenSSL import SSL
import PimLogger as log
import PimPool as pool
import PimOps
import cPickle
from multiprocessing import TimeoutError
import simplejson


class SetSystem(object):
    '''
    Set system (pimCm/Systems/Set/{Id})     
    '''
    def __init__(self,a):
        return

    def __call__(self,environ,start_response):
        req = Request(environ)
        m = req.method
        if m == 'PUT':
            # Only support PUT method, others will be taken as invalid request
            res = cmSetSystem(req)
        else:
            res = Response()
            res.status = 400
            content = []
            content.append("INVALID REQUEST ")
            res.body = '\n'.join(content)
        # set response headers
        res.headerlist = [('Content-type', 'application/json;charset=UTF-8')] 
        return res(environ,start_response)
              

def cmSetSystem(req):
    res = Response()
    token = None
    print("Receive Set Systems Request with pararmters %s %s%s" %(req.body,req.script_name,req.path_info))
    # 1.check Token
    # token may be None, that will cause check failed, don't need to check
    v = PimOps.checkToken(req.environ['HTTP_X_AUTH_TOKEN'])
    if not v:
        #fail to check token
        res.status = 400
        content = []
        content.append('{"Result":"Fail"}')
        res.body = '\n'.join(content)
        return res      
    # 2.check {id}, should NOT be None
    if not req.path_info:
        res.status = 400
        content = []
        content.append('{"Result":"Fail"}')
        res.body = '\n'.join(content) 
        return res
    # 3. send request to PIM side (it MAY TAKE 10+ seconds,be careful with timeout)
    # 3.1 get username/passwd of LXCA from cfg.ini
    username = PimAssist.Config().getValue('PIM_USER')
    password = PimAssist.Config().getValue('PIM_PASS')
    pimIP = PimAssist.Config().getValue('PIM_IP')
    try:
        # set CERT_NONE 
        context = ssl._create_unverified_context()
        conn = httplib.HTTPSConnection(pimIP, context=context)

        # build authorization for LXCA
        user_and_pass = base64.b64encode(username + ':' + password)
        headers = {"Authorization": "Basic %s" % user_and_pass,"Content-type":"application/json", "charset":"UTF-8"}

        conn.request(req.method, req.script_name + req.path_info, req.body, headers)
        pimres = conn.getresponse()
        body = pimres.read()
        print ("Set System Call get response from PIM %s" %(body))

        res.status = pimres.status
    except Exception, exc:
        log.error("Check network connection between PIM and PIM plugin!!!")
        log.exception('Set System call faile, Req header is %s,Req script_name is %s,Req query_string is %s'\
                   %(req.headers.items(),req.script_name,req.query_string))
        res.status = 500
        content = []
        content.append('{"Result":"Fail"}')
        res.body = '\n'.join(content)
        return res
    # 4. send response to NFVO side
    res.status = pimres.status
    res.body = body   
    return res

