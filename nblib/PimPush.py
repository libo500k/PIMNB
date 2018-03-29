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

