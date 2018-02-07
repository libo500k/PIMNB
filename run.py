from webob import Response
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
import webob
from OpenSSL import SSL
import sys
import signal,time,threading
from nblib import *


c = PimAssist.Config()
cert_path =  c.getValue('CERT')
paste_path = c.getValue('PASTE')
 
ctx = SSL.Context(SSL.SSLv23_METHOD)
fpem =  cert_path
ctx.use_privatekey_file (fpem)
ctx.use_certificate_file(fpem)





def CtrlC(signum, frame):
    print 'You choose to stop me.'
    sys.exit()
"""
@wsgify
def application(req):
#   webob.Request.remote_user ==
    return Response('Hello World')


@wsgify.middleware()
def my_filter(req, app):
    # just print a message to the console
    print('my_filter was called')
    return app(req)


def app_factory(global_config, **local_config):
    return application


def filter_factory(global_config, **local_config):
    return my_filter
"""

if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT,CtrlC)
        appname = "pimnb"
        wsgi_app = loadapp(paste_path, appname) 
        #wsgi_app = loadapp(paste_path)
        httpserver.serve(wsgi_app, host='0.0.0.0', port=8080, ssl_context=ctx)
        #httpserver.serve(wsgi_app, host='127.0.0.1', port=8080)
    except Exception, exc:
        print exc
        print '==============================='

