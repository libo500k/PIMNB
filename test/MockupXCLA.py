from webob import Response
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
import webob
from OpenSSL import SSL
import sys
import signal,time,threading
import json
from nblib import *
import datetime
from pprint import pprint
import pdb




@wsgify
def CM(req):
    v = '''
{
  "Version": "1.0",
  "VimId": "81f1d9d0-ca13-4eea-a4ce-9bd89a50c9d1",
  "Chassis": {
    "URL": "/v1//v1/pimCm/Chassis"
  },
  "Systems": {
    "URL": "/v1//v1/pimCm/Systems"
  },
  "Switches": {
    "URL": "/v1//v1/pimCm/Switches"
  },
  "Firewalls": {
    "URL": "/v1//v1/pimCm/Firewalls"
  },
  "DiskArrayChassis": {
    "URL": "/v1//v1/pimCm/DiskArrayChassis"
  },
  "DiskArraySystems": {
    "URL": "/v1//v1/pimCm/DiskArraySystems"
  },
  "StorageServices": {
    "URL": "/v1//v1/pimCm/StorageServices"
  }
} 
    '''
    print ("Received Register callback  with below info:....")  
    pprint(req)
    #pdb.set_trace()
    res = Response()
    res.status = 201
    res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
    res.body = v
    return res 

def DummyCM(global_config, **local_config):
    return CM


if __name__ == '__main__':
    paste_path = "config:/root/PIMNB/PIMNB/test/xcl.ini"
    try:
        appname = "main"
        wsgi_app = loadapp(paste_path,appname)
        httpserver.serve(wsgi_app, host='127.0.0.1', port=2345)

    except Exception, exc:
        print exc
        print '==============================='

