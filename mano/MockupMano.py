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

token = "gAAAAABaj8leBcYcbPf-0fijcTNhoV47TC2nzgOIfqFJQ0irLH4F9OjioH2vzEebuHHcU5a4yOLK_Obx4WhSqHcK4KzwkzR82wRrmYaYAdqMPwf7VS4eBgDpd_1IaX65DuGaReU14DZncPXXlajTvdxTHHJiN-6-jw"

t = datetime.datetime.now().isoformat() 
expired = datetime.datetime.now() + datetime.timedelta(seconds=5)
e = expired.isoformat()
ip = "127.0.0.1:1234"
v = '''{
    "Token": "%s",
    "IssuedAt": "%s",
    "ExpiresAt": "%s",
    "CallBackUris": [
        {
            "UriType": "pimCm",
            "CallBackUri": "https://%s/pimCm"
        },
        {
            "UriType": "pimPm",
            "CallBackUri": "https://%s/pimPm"
        },
        {
            "UriType": "pimFm",
            "CallBackUri": "https://%s/pimFm"
        }
    ]
}''' %(token,t,e,ip,ip,ip)

@wsgify
def application(req):
    t = datetime.datetime.now().isoformat()
    expired = datetime.datetime.now() + datetime.timedelta(seconds=5)
    e = expired.isoformat()
    ip = "127.0.0.1:1234"
    v = '''{
    "Token": "%s",
    "IssuedAt": "%s",
    "ExpiresAt": "%s",
    "CallBackUris": [
        {
            "UriType": "pimCm",
            "CallBackUri": "https://%s/pimCm"
        },
        {
            "UriType": "pimPm",
            "CallBackUri": "https://%s/pimPm"
        },
        {
            "UriType": "pimFm",
            "CallBackUri": "https://%s/pimFm"
        }
    ]
    }''' %(token,t,e,ip,ip,ip)
    pprint(req)
    #pdb.set_trace()
    res = Response()
    res.status = 201
    res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
    res.body = v 
    return res 

def Mockup(global_config, **local_config):
    return application


c = PimAssist.Config()
cert_path =  c.getValue('CERT')
paste_path = c.getValue('PASTE')

ctx = SSL.Context(SSL.SSLv23_METHOD)
fpem =  cert_path
ctx.use_privatekey_file (fpem)
ctx.use_certificate_file(fpem)


if __name__ == '__main__':
    paste_path = "config:/root/mano.ini"
    try:
        appname = "mockup"
        wsgi_app = loadapp(paste_path,appname)
        httpserver.serve(wsgi_app, host='0.0.0.0', port=1234, ssl_context=ctx)

    except Exception, exc:
        print exc
        print '==============================='

