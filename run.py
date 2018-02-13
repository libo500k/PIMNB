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
    #t1.do_run = False
    sys.exit()

if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT,CtrlC)
        PimOps.globalDict.loadDB() 
        # Start a thread timer for AuthForPushData, 1 second
        t1 = threading.Thread(target=PimOps.authForPushData,args=(1,1,))
        t1.start()
        appname = "pimnb"
        wsgi_app = loadapp(paste_path, appname) 
        #wsgi_app = loadapp(paste_path)
        httpserver.serve(wsgi_app, host='0.0.0.0', port=9141, ssl_context=ctx)
        #httpserver.serve(wsgi_app, host='127.0.0.1', port=8080)
    except Exception, exc:
        print "================== ERROR OCCURED=============================="
        print exc
        print "=============================================================="
    finally:
        t1.do_run = False 
        t1.join()
