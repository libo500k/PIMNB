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
import re
import httplib, urllib
import ssl
from multiprocessing import Pool, TimeoutError
import PimLogger as log


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
                #LoadDB and NFVO down will cause there is no "advance" key
                if (c >= stamp+delta) and ('advance' in rundata[key]) :
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
        #Ignore safely of TimeoutError 
        print "timeout"
        log.info("TimeoutError,Ignore Safely,Better to check Network Connection With NFVO")

def cbCMHB(res):
    if res == None :
        log.error("CM Heartbeat Failed, check network connection wiht MANO/NFVO")
    elif ( 200<= res <300):
        print ("CM heartbeat Success,Return Code(%s)"%res)
        log.debug("CM heartbeat Success,Return Code(%s)"%res)
    else:
        log.error("CM Heartbeat Failed, MANO/NFVO return Wrong Code(%s)" %res)

def sendRequestCMHB(node,timeout):
    # id = os.getpid()
    # print (id)
    vimid = PimOps.getVimid()
    # print(node)
    body = '{"Version":"1.0","SrcType":"pim","MsgType":"pimCmHeartbeat","VimId":"%s"}' % vimid
    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": node['advance']['Token']}
    sslctx = ssl._create_unverified_context()
    # fetch the cm heartbeat ip:port or ip only.
    for i in node['advance']['CallBackUris']:
        # !!! Pressed for time, hard-coding PIMCM,re-struct later
        if i['UriType'].upper() == "PIMCM":
            regex = ".+//(.+)/(.+)$"
            if re.search(regex, i['CallBackUri']):
                match = re.search(regex,i['CallBackUri'])
                hosturl = match.group(1)
                restapi = '/'+match.group(2)
                break
            else:
                print("CM HeartBeat Error Occured with wrong URI format %s" %i['CallBackUri'])
                log.error("CM HeartBeat Error Occured with wrong URI format %s" %i['CallBackUri']) 
                return None
    c = httplib.HTTPSConnection(host=hosturl,timeout=timeout,context=sslctx) 
    try:
        c.request("PUT", restapi, body, headers)
        res = c.getresponse()
    except Exception, exc:
        log.exception('CM Heartbeat Error With Failed Connection')
        print exc
        return None
    # Be careful not to return res, it will cause "MaybeEncodingError" exception
    # refer to below link for detail
    # https://stackoverflow.com/questions/21684611/
    return res.status 


