#!/user/bin/env python

"""
PimAgent.py
   : Proxy class for NFV PIM northbound
"""

__author__     = "Li Bo"
__copyright__  = "Copyright 2018, Lenovo Research"


import signal,time,threading
import PimOps 
import datetime
import os
import httplib, urllib
import ssl
from multiprocessing import Pool, TimeoutError


def cmHeartbeat(pool,interval,timeout):
    t = threading.currentThread()
    #pdb.set_trace()
    while getattr(t, "do_run", True):
        changed = False
        rundata = PimOps.globalDict.getCopy()
        # get current time
        c = datetime.datetime.now().replace(tzinfo=None)
        for key in rundata:
            if not rundata[key].has_key('cmstamp'):
                # this case will happen on load db or new register
                # there is no token in rundata, so just set the stamptime 
                rundata[key]['cmstamp'] = str(c) 
                changed = True
            else:
                stamp = PimOps.getDateTimeFromISO8601String(rundata[key]['cmstamp']).replace(tzinfo=None)
                delta = datetime.timedelta(seconds = rundata[key]['basic']['Heartbeat'])
                if  c >= stamp+delta :
                    rundata[key]['cmstamp'] = str(c)
                    # do heartbeat
                    doCMHB(pool,rundata[key],timeout)
                    changed = True

        if changed == True :
            PimOps.globalDict.merge(rundata)
        time.sleep(interval)

def doCMHB(pool, node, timeout):
    res = pool.apply_async(func=sendRequestCMHB,args = (node,timeout),callback = cbCMHB) 
    try:
        res.get(timeout=1)
    except TimeoutError:
        #nothing to do, async call, callback function will handle 
        print "timeout"
    print "-----"

def cbCMHB(res):
    print (res)

def sendRequestCMHB(node,timeout):
    # id = os.getpid()
    # print (id)
    vimid = PimOps.getVimid()
    # print(node)
    body = '{"Version":"1.0","SrcType":"pim","MsgType":"pimCmHeartbeat","VimId":"%s"}' % vimid
    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": node['advance']['Token']}
    sslctx = ssl._create_unverified_context()
    c = httplib.HTTPSConnection(host="127.0.0.1:1234",\
        timeout=timeout,context=sslctx) 
    try:
        c.request("POST", "/pimCm",body, headers)
        res = c.getresponse()
    except Exception, exc:
        log.exception('failed to send request/get response from mano, authforpushdata')
        print exc
    # Be careful not to return res, it will cause "MaybeEncodingError" exception
    # refer to below link for detail
    # https://stackoverflow.com/questions/21684611/
    return res.status 


