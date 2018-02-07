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
    def addBasic(cls,key,value):
        if cls._lock.acquire():
            cls._auth[key] = {}
            cls._auth[key]["basic"] = value
            cls._lock.release()

    

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
            res.status = '400 INVALID REQUEST'
            res.content_type = "text/plain"
            content = []
            content.append(" Error Request : without method ") 
            res.body = '\n'.join(content)  
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
            res.status = '401'
            content = []
            content.append(" Error Request : UNAUTHORIZED ")
            return res
        # retrive request body params
        self.body = json.loads(req.body) 
        v = self._checkIntegrity()
        if not v:
            res.status = '400'
            content = []
            content.append(" Error Request : INVALID REQUEST ") 
            return res
        # save to database
        v = self._saveToDB(req)
        if not v:
            res.status = '500'
            content = []
            content.append(" Error Request :INTERNAL SERVER ERROR ")
            return res 
        # update global dict wich lock
        globalDict.addBasic(req.remote_addr.strip(),self.body)
        # send success response
        res.status = 201
        res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
        res.body = json.dumps({"VimId":self._getVimid()})
        print ( "=====> Subscription from %s ,handled =======" % req.remote_addr)
        return res

    def _deleteSubs(self,req):
        res = Response()
        import pdb
        pdb.set_trace()
        str = req.path_qs
        regex = ".+pimJobs/(.+)\?subType=(.+)"
        if re.search(regex, str):
            match = re.search(regex, str)
            print "Full match: %s" % (match.group(0))
            # So this will print "June"
            print "Month: %s" % (match.group(1))
            # So this will print "24"
            print "Day: %s" % (match.group(2))
        else:
            # wrong query string
            log.error("incorrect delete subscription qs in header")
            res.status = '400'
            content = []
            content.append(" Error Request(d) : INVALID REQUEST ")
            return res
            
        print "=====delete======="
        return res

    def _listSubs(self,req):
        res = Response()
        print "=====get======="
        return res

    def _checkToken(self):
        if not self.token:
            return False
        else:
            # check token with VIM kestone, dummy code
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
    
    def _saveToDB(self,req):
        saved = True
        c = PimAssist.Config()
        dbuser =  c.getValue('DB_USER')
        dbpasswd = c.getValue('DB_PASSWD')
        dbname = c.getValue('DB_NAME')
        dburi = c.getValue('DB_URI')
        db = MySQLdb.connect(dburi,dbuser,dbpasswd,dbname) 
        ip = req.remote_addr.strip()
        nfvoid = self.body.get('NfvoId')
        hb = self.body.get('Heartbeat')
        pe = self.body.get('Period')
        url = self.body.get('IdentityUri')
        user = self.body.get('Username')
        passwd = self.body.get('Password')   
        sql = "INSERT INTO RegMano(ip,nfvoid,heartbeat,period,identityuri,user,passwd)\
               VALUES ('%s','%s',%s,%s,'%s','%s','%s')" % (ip,nfvoid,hb,pe,url,user,passwd) 
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

    @classmethod
    def factory(cls,global_conf,**kwargs):
        return PimJobs()


