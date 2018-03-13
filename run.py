from webob import Response
from webob.dec import wsgify
from paste import httpserver
from paste.deploy import loadapp
import webob
from OpenSSL import SSL
import sys
import signal,time,threading
from nblib import *
from nblib import PimPool as pool


pool.touch()

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
    pool.close()
    pool.terminate()
    pool.join()
    sys.exit()

if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT,CtrlC)
        # initial working process pool 
        PimOps.globalDict.loadDB() 
        # Start a thread timer for AuthForPushData, 1 second
        t1 = threading.Thread(target=PimOps.authForPushData,args=(1,1,))
        t1.start()
        # Start a thread timer for CM and FM heartbead, 1 second
        t2 = threading.Thread(target=PimAgent.cmfmHeartbeat,args=(pool,1,2,))
        t2.start() 
        appname = "pimnb"
        wsgi_app = loadapp(paste_path, appname) 
        # start the rest api service on 9141 port 
        httpserver.serve(wsgi_app, host='0.0.0.0', port=9141, ssl_context=ctx)
        
        # !!! Need to check the thread status like ( t1, t2 ...)
        # if failed, MUST pull it up again       
        # if t1.isAlive():

    except Exception, exc:
        print "================== ERROR OCCURED=============================="
        print exc
        print "=============================================================="
    finally:
        t1.do_run = False 
        t1.join()
        t2.do_run = False
        t2.join()
