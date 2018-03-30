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
    print "*********************************fuck fuck***********************************************"

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





