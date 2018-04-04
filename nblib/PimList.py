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
from multiprocessing import TimeoutError


"""
    ISP list
"""
ISPList=[
"alarmTitle",
"alarmStatus",
"alarmType",
"origSeverity",
"eventTime",
"alarmId",
"msgSeq",
"specificProblemID",
"specificProblem",
"neUID",
"neName",
"neType",
"objectUID",
"objectName",
"objectType",
"locationInfo",
"addInfo",
"PVFlag"
]


"""
    ISP-->LXCA mapping dict
"""
ISP2LXCA_DICT={
"alarmTitle":"msg",
#"alarmStatus":"",
"alarmType":"severityText",
#"origSeverity":"",
"eventTime":"eventDate",
"alarmId":"alertID",
"msgSeq":"msgID",
"specificProblemID":"eventID",
"specificProblem":"eventSourceText",
"neUID":"componentID",
"neName":"systemText",
"neType":'typeText',
"objectUID":"sourceID",
#"objectName":"",
#"objectType":"",
"locationInfo":"location",
#"addInfo":"",
"PVFlag":"pim",
}


"""
LXCA alert array item, please refer to RESP API of LXCA 2.0
"""
LXCAAlertItem = {
    'alertID',
    'args',
    'bayText',
    'chassisText',
    'componentID',
    'componentIdentifierText',
    'eventClass',
    'eventDate',
    'eventID',
    'eventSourceText',
    'failFRUNames',
    'failFRUPartNumbers',
    'failFRUUUIDs',
    'failFRUs',
    'failSNs',
    'fruSerialNumberText',
    'groupName',
    'groupUUID',
    'isManagement',
    'location',
    'msg',
    'msgID',
    'raisedDate',
    'relatedAlerts',
    'service',
    'serviceabilityText',
    'severity',
    'severityText',
    'sourceID',
    'systemFruNumberText',
    'systemName',
    'systemSerialNumberText',
    'systemText',
    'systemTypeModelText',
    'systemTypeText',
    'typeText'
}


class ListResDetails(object):
    '''
    List resource(pimCm)     
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

class ListChassisList(object):
    '''
    List Chassis List(pimCm/Chassis)     
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

class ListSystemList(object):
    '''
    List System List(pimCm/Chassis)     
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
        else:
            res = Response()
            res.status = 400
            content = []
            content.append("INVALID REQUEST ")
            res.body = '\n'.join(content)
        return res(environ,start_response) 

def ListRes(req):
    pimIP = PimAssist.Config().getValue('PIM_IP')
    return RelayRequest(req,pimIP)

def RelayRequest(req,pimIP):
    res = Response()
    #get PIM user and password, base64 coding
    pimuser = PimAssist.Config().getValue('PIM_USER')
    pimpass = PimAssist.Config().getValue('PIM_PASS')
    auth = base64.b64encode(pimuser+ ':'+ pimpass)
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
    c = httplib.HTTPSConnection(host=pimIP,\
        timeout=1,context=ssl._create_unverified_context())

    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "Authorization": "Basic "+ auth}
    try:
        if req.path_info:
            p = req.script_name + req.path_info + "?" + req.query_string
        else:
            p = req.script_name + "?" + req.query_string
        c.request(req.method, p , None, headers)
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


"""
    ListActiveAlarm(pimFm) class, proxy to PIM backend with process pool

    PIMNB request                       https://127.0.0.1:9141/v1/pimFm/ListActiveAlarms
    redirecting to LXCA's REST API:     https://<PIM_IP>/events/activeAlerts
""" 
class ListActiveAlarms(object):
    def __init__(self, a):
        return

    def __call__(self, environ, start_response):
        req = Request(environ)
        m = req.method
        if m == 'GET':
            res = doListActiveAlarm(req)
            return res(environ,start_response) 


"""
    doListActiveAlarm
"""
def doListActiveAlarm(req):
    pimIP = PimAssist.Config().getValue('PIM_IP')
    # relay ListActiveAlarm to LXCA
    return RelayListActiveAlarm(req, pimIP)


"""
    Data mapping from LXCA_Resp -> ISP_Rep
"""
def LXCA2ISP_DataMapping(LXCA_resp, targetList, mapDict):

    # convert LXCA_resp string to json
    #obj_dump = json.dumps(LXCA_resp)
    obj_json = json.loads(LXCA_resp)

    vimid = PimOps.getVimid()

    # ISPList
    targetList = ISPList
    # mapping dict
    mapDict= ISP2LXCA_DICT

    keyHit = True
    alarmList=[]

    # FIXME: only support less than 500 now
    for i in obj_json:
        alarmList.append("{")

        for k in targetList:

            if k in mapDict.keys():
                mapping = mapDict[k]
                keyHit = True
            else:
                mapping = ""
                keyHit = False

            v =""
            if keyHit:
                if mapping in i:
                    v = i[mapping]
                else:
                    # default value, e.g. PVFlag 
                    v = mapDict[k]
            
            # check if the last one in list
            if k is not targetList[-1]:
                alarmItem = '"%s": "%s",' % (k,v)
            else:
                alarmItem = '"%s": "%s"' % (k,v)

            alarmList.append(alarmItem)
            #print alarmItem

        alarmList.append( "}")

    alarmBody = "".join(alarmList)
    body = '{"Version":"1.0", "VimId":"%s", "SrcType":"pim", "MsgType":"pimFmAlarm", "AlarmList":"[%s]", "CurrentBatch": 1, "TotalBatches": 1}' % (vimid, alarmBody)

    return body


"""
    Relay ListActiveAlarm request to LXCA
"""
def RelayListActiveAlarm(req, pimIP):

    # get username/passwd of LXCA from cfg.ini
    username = PimAssist.Config().getValue('PIM_USER')
    password = PimAssist.Config().getValue('PIM_PASS')
    LAA_url = "/events/activeAlerts"
    lxca_url = 'https://%s%s' % (pimIP, LAA_url)

    res = Response()

    try: 
        # set CERT_NONE 
        context = ssl._create_unverified_context()
        conn = httplib.HTTPSConnection(pimIP, context=context)

        # build authorization for LXCA
        user_and_pass = base64.b64encode(username + ':' + password)
        headers = {"Authorization": "Basic %s" % user_and_pass,"Content-type":"application/json", "charset":"UTF-8"}

        conn.request(req.method, lxca_url, headers=headers)
        pimres = conn.getresponse()


        res.status = pimres.status
        body = pimres.read()
        # pdb.set_trace()
        res.text = LXCA2ISP_DataMapping(body, ISPList, ISP2LXCA_DICT)

        # PIM connection is OK, but API failed
        checkPimResStatus(pimres)
    except (httplib.HTTPException, socket.timeout, socket.gaierror, Exception), e:
        log.error("Check network connection between PIM and PIM plugin!!!")
        log.error('lxca_url %s is unreachable, Exception %s %s' % (lxca_url, e.__class__.__name__, e))
        print 'lxca_url %s is unreachable, Exception %s %s' % (lxca_url.encode('utf-8'), e.__class__.__name__, e)
        res.status = 500
        content = []
        content.append("Relay Request Error: failed to get response from PIM")
        res.body = '\n'.join(content)

    return res


"""
    ListHistoryAlarm(pimFm) class, proxy to PIM backend with process pool

    PIMNB request                       https://127.0.0.1:9141/v1/pimFm/ListHisAlarms
    redirecting to LXCA's REST API:     https://<PIM_IP>/events/??
""" 
class ListHistoryAlarms(object):
    def __init__(self, a):
        return

    def __call__(self, environ, start_response):
        req = Request(environ)
        m = req.method
        if m == 'GET':
            res = doListHistoryAlarm(req)
            return res(environ,start_response) 

"""
    doListHistoryAlarm
"""
def doListHistoryAlarm(req):
    pimIP = PimAssist.Config().getValue('PIM_IP')
    # relay ListActiveAlarm to LXCA
    return RelayListHistoryAlarm(req, pimIP)


"""
    Relay ListHistoryAlarm request to LXCA
"""
def RelayListHistoryAlarm(req, pimIP):

    # get username/passwd of LXCA from cfg.ini
    username = PimAssist.Config().getValue('PIM_USER')
    password = PimAssist.Config().getValue('PIM_PASS')
    LAA_url = "/events/activeAlerts"
    lxca_url = 'https://%s%s' % (pimIP, LAA_url)

    res = Response()

    try: 
        # set CERT_NONE 
        context = ssl._create_unverified_context()
        conn = httplib.HTTPSConnection(pimIP, context=context)

        # build authorization for LXCA
        user_and_pass = base64.b64encode(username + ':' + password)
        headers = {"Authorization": "Basic %s" % user_and_pass,"Content-type":"application/json", "charset":"UTF-8"}

        conn.request(req.method, lxca_url, headers=headers)
        pimres = conn.getresponse()


        res.status = pimres.status
        body = pimres.read()
        # pdb.set_trace()
        res.text = LXCA2ISP_DataMapping(body, ISPList, ISP2LXCA_DICT)

        # PIM connection is OK, but API failed
        checkPimResStatus(pimres)
    except (httplib.HTTPException, socket.timeout, socket.gaierror, Exception), e:
        log.error("Check network connection between PIM and PIM plugin!!!")
        log.error('lxca_url %s is unreachable, Exception %s %s' % (lxca_url, e.__class__.__name__, e))
        print 'lxca_url %s is unreachable, Exception %s %s' % (lxca_url.encode('utf-8'), e.__class__.__name__, e)
        res.status = 500
        content = []
        content.append("Relay Request Error: failed to get response from PIM")
        res.body = '\n'.join(content)

    return res
