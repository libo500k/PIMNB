#!/user/bin/env python

"""
PimPush.py
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


"""
    EventID list for Resoure Change
"""
RES_CHG_EVENTID=[
'FQXHMDI0101I',     # DelRes
'FQXHMDI0102I',     # AddRes
'FQXSPEM4017I'      # UpdateRes
]


class ListTest(object):
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



def ListRes(req):
    pimIP = PimAssist.Config().getValue('PIM_IP')
    return RelayRequest(req,pimIP)

def RelayRequest(req,pimIP):
    res = Response()
    v = persistence("BJ-NFVO-0","127.0.0.1:2345","<json>/hello</json>","PUT","/v1/pimCm")
    print v
    rows = getFailedRecords() 
    for each in rows:
        t = each[1]
        #delRecord(t)
    return res

# Saved return True, else return False
def persistence(nfvoid ,failip, failbody, failmethod,failuri):
    print(failip,failbody,failmethod,failuri)
    saved = True
    t = int(time.time()*100)
    body = cPickle.dumps(failbody)
    sql = """INSERT INTO persistence (nfvoid,failtime,failip,failbody,failmethod,failuri) VALUES(%s,%s,%s,%s,%s,%s);"""
    data = (nfvoid,t,failip,body,failmethod,failuri)
    try:
        db = PimOps.connectDB()
        cursor = db.cursor()
        cursor.execute(sql,data)
        db.commit()
    except:
        saved = False
        db.rollback()
        log.exception('failed to save persistence data into database')
    finally:
        db.close()
    return saved
"""
    Get failed records from database, return list
"""
def getFailedRecords():
    sql = """SELECT * from persistence;"""  
    try:
        db = PimOps.connectDB()
        cursor = db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
    except:
        log.exception('failed to load failed records from database, check database configuraiton!')
    finally:
        db.close()
    return rows

def delRecord(ftime):
    deleted = True
    sql = """DELETE from persistence where failtime=%s;"""
    try:
        db = PimOps.connectDB()
        cursor = db.cursor()
        cursor.execute(sql,[ftime])
        db.commit()
    except:
        log.exception('failed to delete failed record!')
        deleted = False
    finally:
        db.close()
    return deleted
"""
    entry function of re-play failed records 
"""
def replay(interval, timeout):

    t = threading.currentThread()
    while getattr(t, "do_run", True):
        # get failed records from backend database
        rows = getFailedRecords()
        # get current Token from global variable "rundata"
        # if there is no "active" segment in "rundata", just ignore this line.
        # it will be handled in next cycle
        rundata = PimOps.globalDict.getCopy()
        for each in rows:
            nfvoid = each[0]
            print "nfvoid = %s" %nfvoid
            if not nfvoid in rundata:
                print "failed to find the registered NFVO (%s)info, skip" %nfvoid
                continue
            else: 
                # extract TOKEN, and try to rebuild request, send again
                if not rundata[nfvoid].has_key('advance'):
                    print "failed to extract TOKEN (%s), skip, wait for next time" %nfvoid                
                    continue
                else:
                    t = rundata[nfvoid]['advance']['Token']
                    ftime = each[1]
                    fip = each[2]
                    fbody = each[3]
                    fmethod = each[4]
                    furi = each[5]
                    print "NFVO(%s) Token(%s) Time(%s) IP(%s) URI(%s)" %(nfvoid,t,ftime,fip,furi)
                    r = sendFailedRequest(t,fip,fbody,fmethod,furi) 
                    print "Failed Record resend status %s" %(r)
                    # delete records from database if resend successfully
                    if 199 <r <300:
                        delRecord(ftime)
                        print "delete records from database cause resend action success"
        # sleep 
        # time.sleep(interval)
        time.sleep(5)
    print "*********************************end of t3 thread***********************************************"

def sendFailedRequest(t,fip,fbody,fmethod,furi):
    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": t}
    c = httplib.HTTPSConnection(host=fip,\
        timeout=1,context=ssl._create_unverified_context())
    try:
        b = cPickle.loads(str(fbody)) 
        c.request(fmethod, furi, b, headers)
        res = c.getresponse()
    except Exception, exc:
        log.exception("failed to resend failed records")
        print exc
        return 500
    return res.status






"""
    Processing push from lxca, current support PushAlarm & PushResChg
"""
def doRelayPush(req):

    # prepare for relay event
    body  = req.body
    method = req.method # POST only now, maybe should support PUSH later
    nfvoIp = ''
    uri = ''

    # set default value
    res = Response()
    res.status = 200
    bERROR = True
    bAlarm = True

    # current only support Alarm_Event and ResChg_Event
    eventDict = simplejson.loads(body)
    if eventDict['eventID'] in RES_CHG_EVENTID:
        bAlarm = False


    # get a local copy of rundata
    rundata = PimOps.globalDict.getCopy() 

    # relay to nfvo, maybe multiple nfvo, identified by nfvoId
    for nfvoId in rundata:

        # for a specific nfvo
        node = rundata[nfvoId]
        if rundata[nfvoId].has_key('advance'):

            for i in node['advance']['CallBackUris']:
                # alarm event
                if bAlarm:
                    if i['UriType'].upper() == "PIMFM":
                        regex = ".+//(.+)/(.+)$"
                        if re.search(regex, i['CallBackUri']):
                            match = re.search(regex,i['CallBackUri'])
                            nfvoIp = match.group(1)
                            uri = '/'+match.group(2)
                            break
                        else:
                            log.error("Error Occured with wrong URI format %s" % i['CallBackUri'])
                # resouce chg event
                else:
                    if i['UriType'].upper() == "PIMCM":
                        regex = ".+//(.+)/(.+)$"
                        if re.search(regex, i['CallBackUri']):
                            match = re.search(regex,i['CallBackUri'])
                            nfvoIp = match.group(1)
                            uri = '/'+match.group(2)
                            break
                        else:
                            log.error("Error Occured with wrong URI format %s" % i['CallBackUri'])

            # get token before push
            token = node['advance']['Token']

            # build auth header 
            headers = { "X-Auth-Token" : token }

             # relay to nfvo i # loop for multiple NFVO
            conn = httplib.HTTPSConnection(host=nfvoIp,\
                    timeout=1, context=ssl._create_unverified_context())

            try:
                conn.request(method, nfvoIp + uri, body=body, headers=headers)
                nfvo_res = conn.getresponse()
                res.status = nfvo_res.status
            except Exception, exc:
                # fail to relay to nfvo
                log.error("Check network connection between PIMNB and NFVO!!!")
                log.exception('Req header is %s,Req script_name is %s,Req query_string is %s'\
                           %(req.headers.items(),req.script_name,req.query_string))
                print ('Req header is %s,Req script_name is %s,Req query_string is %s'\
                           %(req.headers.items(),req.script_name,req.query_string))
            else:
                # no exception
                if res.status == 200:
                    # no error
                    bERROR = False
            finally:
                if bERROR:
                    # failed to push data to nfvo
                    if persistence(nfvoId, nfvoIp, body, method, uri):
                        print "Fail to relay to NFVO, save to db"
                        log.error("Fail to relay to NFVO, save to db")
                    else:
                        log.error("Fail to relay to NFVO, and failed to save to db")
                        #FIXME: maybe db crashed? or disk full?
                        # only in this case, return res.status as 500 
                        res.status = 500
                        content = []
                        content.append("RelayPush Error: failed to replay push data to NFVO")
                        res.body = '\n'.join(content)

        else:
            # no info in rundata
            log.error("RelayPush Error: no advance section found in rundata")
            res.status = 500
            content = []
            content.append("RelayPush Error: no advance section found in rundata!")
            res.body = '\n'.join(content)

    return res


"""
    RelayPush(pimPush) class, relay push data NFVO

    psuh data from lxca                 https://127.0.0.1:9141/v1/pimPush
    redirecting to NFVO's REST API:     https://<NFVO_IP>/pimCm (PushResChg) or https://<NFVO_IP>/pimFm (PushAlarm)
""" 
class RelayPush(object):
    def __init__(self, a):
        return

    def __call__(self, environ, start_response):
        req = Request(environ)
        m = req.method
        if m == 'POST':
            res = doRelayPush(req)
            return res(environ, start_response) 
