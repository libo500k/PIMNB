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
import PimAssist
import re
import copy

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
        import pdb
        pdb.set_trace()
        sql = "select * from RegMano" 
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
        self.vimid = None
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
        v = self._checkToken()
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
        res.body = json.dumps({"VimId":self._getVimid()})
        print ( "=====> Subscription from %s ,handled =======" % req.remote_addr)
        return res

    def _deleteSubs(self,req):
        res = Response()
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
        v = self._checkToken()
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

    def _checkToken(self):
        if not self.token:
            return False
        else:
            # check token with VIM kestone, dummy code
            print "check token dummy : %s" % self.token
            return True
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
        return True

    def _getVimid(self):
        if not self.vimid:
            self.vimid = "dummy vimid 123"
        return self.vimid

    def _deleteFromDB(self,nfvoid):
        deleted = True
        c = PimAssist.Config()
        dbuser =  c.getValue('DB_USER')
        dbpasswd = c.getValue('DB_PASSWD')
        dbname = c.getValue('DB_NAME')
        dburi = c.getValue('DB_URI')
        db = MySQLdb.connect(dburi,dbuser,dbpasswd,dbname)    
        sql = "delete from RegMano where nfvoid= '%s';" %(nfvoid)
        try:
            cursor = db.cursor()
            n = cursor.execute(sql)
            db.commit()
        except:
            deleted = False
            db.rollback()
            log.exception('failed to delete subscription data from database')
        finally:
            if n != 1:
                deleted = False
            db.close()
        return deleted 

        
    def _saveToDB(self,req):
        saved = True
        c = PimAssist.Config()
        dbuser =  c.getValue('DB_USER')
        dbpasswd = c.getValue('DB_PASSWD')
        dbname = c.getValue('DB_NAME')
        dburi = c.getValue('DB_URI')
        db = MySQLdb.connect(dburi,dbuser,dbpasswd,dbname) 
        nfvoid = self.body.get('NfvoId')
        hb = self.body.get('Heartbeat')
        pe = self.body.get('Period')
        url = self.body.get('IdentityUri')
        user = self.body.get('Username')
        passwd = self.body.get('Password')   
        sql = "INSERT INTO RegMano(nfvoid,heartbeat,period,identityuri,user,passwd)\
               VALUES ('%s',%s,%s,'%s','%s','%s')" % (nfvoid,hb,pe,url,user,passwd) 
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
    db = MySQLdb.connect(dburi,dbuser,dbpasswd,dbname) 
    return db

