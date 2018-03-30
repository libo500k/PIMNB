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



token="gAAAAABavgAHDaC17S4paoq20GXc7LHBC89z_An6AFG7LSx3HFrrYX7U-OE0HJFGk8PsQMUNMXk-y_jqNGwqaqqWS8gh_Nv-iADiMtsxOyCpihowEcy50XqP2A8MPoN6CeZyiW3mkK4ZWyGse4be-F1DoatFvpw8ng"
@wsgify
def appl(req):
    t = datetime.datetime.now().isoformat()
    expired = datetime.datetime.now() + datetime.timedelta(seconds=15)
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
    print ("Received Register callback  with below info:....")  
    pprint(req)
    #pdb.set_trace()
    res = Response()
    res.status = 201
    res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
    res.body = v
    return res 

@wsgify
def CM(req):
    m = req.method
    print ("Received CM heartbeat with below info:.%s..." %m)
    pprint(req.body)

    res = Response()
    res.status = 201
    res.headerlist = [('Content-type', 'application/json'),('Charset', 'UTF-8')]
    res.body = "nothing needed"
    return res


def Mockup(global_config, **local_config):
    return appl


def DummyCM(global_config, **local_config):
    return CM


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
        appname = "main"
        wsgi_app = loadapp(paste_path,appname)
        httpserver.serve(wsgi_app, host='0.0.0.0', port=1234, ssl_context=ctx)

    except Exception, exc:
        print exc
        print '==============================='

