#!/user/bin/env python

"""
PimOps.py
   : Operation class for NFV PIM northbound
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


from webob import Response
from webob import Request
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
from OpenSSL import SSL
import PimLogger as log

class globalDict(object):
    _auth = {} 
    _lock = threading.Lock() 

    @classmethod
    def loadDB(cls):
        loaded = True
        db = connectDB()
        sql = "select * from regmano" 
        try:
            cursor = db.cursor()
            cursor.execute(sql)
            # re-strct runtime data
            results = cursor.fetchall()
            # no need to protect global data with lock
            # this func is called in the beginning of daemon
            for row in results:
               d = {}
               d['NfvoId'] = row[0]
               d['Heartbeat'] = row[1]
               d['Period'] = row[2]
               d['IdentityUri'] = row[3]
               d['Username'] = row[4]
               d['Password'] = row[5]
               d['qType'] = "pim" 
               cls._auth[row[0]]={}
               cls._auth[row[0]]["basic"] = d
        except:
            loaded = False
            log.exception('failed to load data from database')
        finally:
            db.close()  
        return loaded
    @classmethod
    def getCopy(cls):
        cls._lock.acquire()
        copied = copy.deepcopy(cls._auth)
        cls._lock.release()
        return copied
    @classmethod
    def merge(cls,d2):
        cls._lock.acquire()
        #Dict update method CANN'T be used in this case
        #There may have items has been deleted during housekeeping sporadically.
        #cls._auth.update(d2)        
        for (k,v) in d2.items():
            if k in cls._auth:
                cls._auth[k] = v
          
        print json.dumps(cls._auth, sort_keys=True, indent=2) 
        cls._lock.release()
 
    @classmethod
    def addBasic(cls,key,value):
        if cls._lock.acquire():
            cls._auth[key] = {}
            cls._auth[key]["basic"] = value
            cls._lock.release()

    @classmethod
    def removeBasic(cls,key):
        try:
            del cls._auth[key]  
        except:
            return False
        return True 

class PimJobs(object):
    '''
    Subscription Class     
    '''
    def __init__(self,a):
        return

    def __call__(self,environ,start_response):
        req = Request(environ)
        m = req.method
        if m == 'GET':
            # list subscription handler for GET method
            res = self._listSubs(req)
        elif m == 'POST':
            # subscription handler for POST method
            res = self._createSubs(req)
        elif m == 'DELETE':
            # delete subscription handler for delete  method
            res = self._deleteSubs(req)
        else:
            # error handler 
            res = Response()
            self._setErrorResponse(res,400,"INVALID REQUEST")
        return res(environ,start_response)

    def _createSubs(self,req):
        res = Response() 
        # get the token from request header 
        self.token = None
        for i in req.headers.items():
            if i[0] == "X-Auth-Token":
                self.token = i[1]
                break
        v = checkToken(self.token)
        if not v:
            #fail to check token
            self._setErrorResponse(res,401,"UNAUTHORIZED")  
            return res
        # retrive request body params
        self.body = json.loads(req.body) 
        v = self._checkIntegrity()
        if not v:
            self._setErrorResponse(res,400,"INVALID REQUEST")
            return res
        # save to database
        v = self._saveToDB(req)
        if not v:
            self._setErrorResponse(res,500,"INTERNAL SERVER ERROR")
            return res 
        # update global dict wich lock
        globalDict.addBasic(self.body['NfvoId'],self.body)
        # send success response
        res.status = 201
        res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
        res.body = json.dumps({"PimId":getVimid()})
        print ( "=====> Subscription from %s ,handled =======" % req.remote_addr)
        return res

    def _deleteSubs(self,req):
        res = Response()
        # check token
        v = checkToken(self.token)
        if not v:
            #fail to check token
            self._setErrorResponse(res,401,"UNAUTHORIZED")
            return res
        # fetch nfvoid
        str1 = req.path_qs
        regex = ".+pimJobs/(.+)\?subType=(.+)"
        if re.search(regex, str1):
            match = re.search(regex, str1)
            nfvoid = match.group(1)
	    qtype = match.group(2)
            #remove from database
            v = self._deleteFromDB(nfvoid) 
            if not v:
                self._setErrorResponse(res,400,"INVALID REQUEST")
                return res
            #update runtime data, doesn't check return value, removed already from database
            globalDict.removeBasic(nfvoid)
            #send response
            res.status = 204
            res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
        else:
            # wrong query string
            self._setErrorResponse(res,400,"INVALID REQUEST")
            log.error("incorrect delete subscription qs in header")
            return res
        print ( "=====> Delete Subscription from %s ,handled =======" % req.remote_addr)
        return res

    def _listSubs(self,req):
        res = Response()
        # get the token from request header 
        self.token = None
        for i in req.headers.items():
            if i[0] == "X-Auth-Token":
                self.token = i[1]
                break
        v = checkToken(self.token)
        if not v:
            #fail to check token
            self._setErrorResponse(res,401,"UNAUTHORIZED")
            return res
 
        str1 = req.path_qs
        regex = ".+\?NfvoId=(.+)\&.+"
        if re.search(regex, str1):
            match = re.search(regex, str1)
            nfvoid = match.group(1) 
            # get data from runtime data
            rundata = globalDict.getCopy() 
            if nfvoid in rundata:
                # get data for response
                res.status = 200
                res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
                res.body = json.dumps(rundata[nfvoid]['basic'])
            else:
                self._setErrorResponse(res,400,"INVALID REQUEST")
                log.error("incorrect query , no runtime data!")  
        else:
            # wrong query string
            self._setErrorResponse(res,400,"INVALID REQUEST")
            log.error("incorrect query  subscription in header")
            return res
        print ( "=====> List Subscription from %s ,handled =======" % req.remote_addr) 
        return res

    def _checkIntegrity(self):
	if not self.body.has_key('NfvoId'):
            return False
        if not self.body.has_key('Username'):
            return False
        if not self.body.has_key('Password'):
            return False
        if not self.body.has_key('IdentityUri'):
            return False
        if not self.body.has_key('subType'):
            return False
        if not self.body.has_key('Period'):
            return False
        if not self.body.has_key('Heartbeat'):
            return False
        if not self.body.has_key('HeartbeatCm'):
            return False
        if not self.body.has_key('HeartbeatFm'):
            return False
        return True

    def _deleteFromDB(self,nfvoid):
        deleted = True
        db = connectDB()    
        sql = "delete from regmano where nfvoid= '%s';" %(nfvoid)
        try:
            cursor = db.cursor()
            n = cursor.execute(sql)
            db.commit()
        except:
            deleted = False
            db.rollback()
            log.exception('failed to delete subscription data from database')
        finally:
            db.close()
        return deleted 

        
    def _saveToDB(self,req):
        saved = True
        db = connectDB() 
        nfvoid = self.body.get('NfvoId')
        hb = self.body.get('Heartbeat')
        pe = self.body.get('Period')
        url = self.body.get('IdentityUri')
        user = self.body.get('Username')
        passwd = self.body.get('Password')   
        hbcm = self.body.get('HeartbeatCm')
        hbfm = self.body.get('HeartbeatFm')
        sql = "INSERT INTO regmano(nfvoid,heartbeat,period,hbcm,hbfm,identityuri,luser,lpasswd)\
               VALUES ('%s',%s,%s,%s,%s,'%s','%s','%s')" % (nfvoid,hb,pe,hbcm,hbfm,url,user,passwd) 
	try:
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except:
            saved = False
            db.rollback()
            log.exception('failed to save subscription data into database')
        finally:
            db.close()
        return saved

    def _setErrorResponse(self,res,s,m):
        res.status = s
        content = []
        content.append(" Error Request : %s" %m)
        res.body = '\n'.join(content)
        return res 

    @classmethod
    def factory(cls,global_conf,**kwargs):
        return PimJobs()


def connectDB():
    c = PimAssist.Config()
    dbuser =  c.getValue('DB_USER')
    dbpasswd = c.getValue('DB_PASSWD')
    dbname = c.getValue('DB_NAME')
    dburi = c.getValue('DB_URI')
    dbtype = c.getValue('DB_TYPE')
    if dbtype=='POSTGRE':
        db = psycopg2.connect(database=dbname, user=dbuser, password=dbpasswd, host=dburi)
    else:
        db = MySQLdb.connect(dburi,dbuser,dbpasswd,dbname)
    return db

def getVimid():
    # Not sure where to get the VIMID based on the SPEC
    # Per Michael and Li Gong's suggestion, use hardcoding as workaround.
    #c = PimAssist.Config()
    #ip = c.getValue('KS_AUTH_IP') 
    #vimid = uuid.uuid5(uuid.NAMESPACE_URL,ip)
    vimid = "81f1d9d0-ca13-4eea-a4ce-9bd89a50c9d1"
    return str(vimid)


def authForPushData(interval,timeout):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        changed = False
        rundata = globalDict.getCopy() 
        #print "===============authforpushdata================="
        for key in rundata:
            if rundata[key].has_key('advance'):
               # print(key+':'+rundata[key]['basic']['IdentityUri']) 
               # if expired, pull new data from mano again
               c = datetime.datetime.now().replace(tzinfo=None)
               t_str = rundata[key]['advance']['ExpiresAt']
               e = getDateTimeFromISO8601String(t_str).replace(tzinfo=None) 
               if  c >= e :
                   data = sendRequestPD(rundata[key]['basic'],timeout)
                   if data != None :
                       rundata[key]['advance'] = json.loads(data)
                       changed = True
            else:
                #print(key+':'+rundata[key]['basic']['IdentityUri']) 
                data = sendRequestPD(rundata[key]['basic'],timeout)
                if data != None :
                    rundata[key]['advance'] = json.loads(data) 
                    changed = True
        #print json.dumps(rundata, sort_keys=True, indent=2)
        if changed == True :
            globalDict.merge(rundata) 
        time.sleep(interval)

def sendRequestPD(info,to):
    #prepare header and body
    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Username":info['Username'],"X-Auth-Password":info['Password']}
    body = '{"PimId": "%s"}' % getVimid()
    #prepare hosturl
    uri = info['IdentityUri']
    regex = ".+//(.+)/(.+)$"
    if re.search(regex, uri):
        match = re.search(regex,uri)
        hosturl = match.group(1)
        restapi = '/'+match.group(2) 
    else:
        log.error("AuthForPushData has wrong callback uri %s" %uri)
        return None
    c = httplib.HTTPSConnection(host=hosturl,\
        timeout=to,context=ssl._create_unverified_context())  
    try:
        c.request("POST", restapi ,body, headers)
        res = c.getresponse()
    except Exception, exc:
        log.exception('Authforpushdata Failed,Check connection with NFVO')
        print ('Authforpushdata Failed,Check connection with NFVO')
        return None
    else:
        # check response status (must be 201)
        if ( res.status != 201 ):
            log.error("AuthForPushData get wrong https response status: %s" %res.status)
            return None
        data = res.read()
        return data 

def getDateTimeFromISO8601String(s):
    d = dateutil.parser.parse(s)
    return d

def checkToken(token):
    if not token:
        return False
    else:
        # check token on VIM kestone
        print "check token : %s" %token
        c = PimAssist.Config()
        ip =  c.getValue('KS_AUTH_IP')
        headers = {"X-Auth-Token":token}
        conn = httplib.HTTPConnection(host=ip, timeout=3)
        try:
            conn.request("GET", "/v2.0/tenants",None,headers)
            res = conn.getresponse()
        except Exception, exc:
            log.exception('failed to verify the token')
            print exc
            return False
        else:
            # check response status (must be 2XX)
            if ( 200<= res.status <299 ):
                return True
            else:
                log.error("Keystone Error Response status: %s" %res.status)
                return False 
