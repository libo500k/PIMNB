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
    v = persistence(req.remote_addr,"<json>/hello</json>",req.method,req.path_qs)
    print v
    getFailedRecords() 
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

def getFailedRecords():
    sql = """SELECT * from persistence;"""  
    try:
        db = PimOps.connectDB()
        cursor = db.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        for each in rows:
            print" ==============**************++++++++++++++++^^^^^^^^^^^^^^^^^^"
            print "time %s" %each[0]
            print "ip %s" %each[1]
            print "body %s" %cPickle.loads(str(each[2]))
    except:
        log.exception('failed to load failed records from database, check database configuraiton!')
    finally:
        db.close()

"""
    entry function of re-play failed records 
"""
def replay(interval, timeout):

    t = threading.currentThread()

    while getattr(t, "do_run", True):
       
        # get failed records from backend database
        getFailedRecords()
        # get current Token from global variable "rundata"
        # if there is no "active" segment in "rundata", just ignore this line.
        # it will be handled in next cycle
        rundata = PimOps.globalDict.getCopy()
        print "..."
        
        time.sleep(interval)


"""
    Processing push from lxca, e.g. PushAlarm, PushResChg
"""
def doRelayPush(req):

    body  = req.body
    method = req.method # POST only now, maybe should support PUSH later
    nfvoIp = ''
    uri = ''

    res = Response()
    res.status = 200
    bERROR = True

    # get a local copy of rundata
    rundata = PimOps.globalDict.getCopy() 
    # relay to nfvo, maybe multiple nfvo, identified by nfvoId
    for nfvoId in rundata:

        if rundata[nfvoId].has_key('advance'):

            # get NFVOIP and uri
            nfvoIp = rundata[nfvoId]['advance']['nfvoip']
            uri = rundata[nfvoId]['advance']['uri']

            # get token before push
            token = rundata[nfvoId]['advance']['token']

            # build auth header 
            headers = { "X-Auth-Token" : token }

             # relay to nfvo i # loop for multiple NFVO
            conn = httplib.HTTPSConnection(host=nfvoIp,\
                    timeout=1, context=ssl._create_unverified_context())

            try:
                conn.request(method, nfvoIp + uri, body=body, headers=headers)
                nfvo_res = c.getresponse()
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
