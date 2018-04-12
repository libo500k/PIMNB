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
from webob import Response
from webob import Request


"""
    Global heartbeat type dict
"""
HB_Dict = {
    "CMHB":"pimCmHeartbeat",
    "FMHB":"pimFmHeartbeat"
}

RESTPATH_HB_Dict = {
    "CMHB":"pimCm",
    "FMHB":"pimFm"
}

"""
    entry function of config management heartbeat (CMHB) and fault management heartbeat (FMHB) thread
"""
def cmfmHeartbeat(pool, interval, timeout):

    t = threading.currentThread()

    while getattr(t, "do_run", True):
        changed = False
        rundata = PimOps.globalDict.getCopy()
        # get current time
        c = datetime.datetime.now().replace(tzinfo=None)
        for key in rundata:
            if rundata[key]['basic']['HeartbeatCm'] == 0:
                continue
            if not rundata[key].has_key('cmstamp'):
                # this case will happen on load db or new register
                # there is no token in rundata, so just set the stamptime 
                rundata[key]['cmstamp'] = str(c) 
                changed = True
            else:
                stamp = PimOps.getDateTimeFromISO8601String(rundata[key]['cmstamp']).replace(tzinfo=None)
                delta = datetime.timedelta(seconds = rundata[key]['basic']['HeartbeatCm'])
                #LoadDB and NFVO down will cause there is no "advance" key
                if (c >= stamp+delta) and ('advance' in rundata[key]) :
                    rundata[key]['cmstamp'] = str(c)
                    # do config management heartbeat
                    doHB(pool, rundata[key], timeout, "CMHB")
                    changed = True

        for key in rundata:
            if rundata[key]['basic']['HeartbeatFm'] == 0:
                continue
            if not rundata[key].has_key('fmstamp'):
                # this case will happen on load db or new register
                # there is no token in rundata, so just set the stamptime 
                rundata[key]['fmstamp'] = str(c)
                changed = True
            else:
                stamp = PimOps.getDateTimeFromISO8601String(rundata[key]['fmstamp']).replace(tzinfo=None)
                delta = datetime.timedelta(seconds = rundata[key]['basic']['HeartbeatFm'])
                #LoadDB and NFVO down will cause there is no "advance" key
                if (c >= stamp+delta) and ('advance' in rundata[key]) :
                    rundata[key]['fmstamp'] = str(c)
                    # do fault management heartbeat
                    doHB(pool, rundata[key], timeout, "FMHB")
                    changed = True

        if changed == True:
            PimOps.globalDict.merge(rundata)
        time.sleep(interval)


"""
    heartbeat processing function based on its type
"""
def doHB(pool, node, timeout, hb_type):

    hb_callback_function_wrapper = lambda res: hb_callback_function(res, hb_type)
    res = pool.apply_async(func=sendHeartBeat, args = (node, timeout, hb_type), callback = hb_callback_function_wrapper)

    try:
        res.get(timeout=1)
    except TimeoutError:
        #nothing to do, async call, callback function will handle 
        #Ignore safely of TimeoutError 
        print "timeout"
        log.info("TimeoutError,Ignore Safely,Better to check Network Connection With NFVO")


"""
    callback function of apply_async based on heartbeat type
"""
def hb_callback_function(res, hb_type):
    if res == None :
        log.error("%s Failed, check network connection wiht MANO/NFVO" % hb_type)
    elif ( 200<= res <300):
        print ("%s Success,Return Code(%s)" %(hb_type, res))
        log.debug("%s Success,Return Code(%s)" %(hb_type, res))
    else:
        log.error("%s Failed, MANO/NFVO return Wrong Code(%s)" % (hb_type, res))


"""
    send heart beat based on its type
"""
def sendHeartBeat(node, timeout, hb_type):
    # id = os.getpid()
    # print (id)
    vimid = PimOps.getVimid()
    # print(node)

    if hb_type in HB_Dict:
        body = '{"Version":"1.0", "PimId":"%s", "SrcType":"vpim", "MsgType":"%s" }' % (vimid, HB_Dict[hb_type])
    else:
        print("Wrong heartbeat type")
        log.error("Wrong heartbeat type")
        return None

    headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": node['advance']['Token']}
    sslctx = ssl._create_unverified_context()
    # fetch the heartbeat ip:port or ip only.
 
    for i in node['advance']['CallBackUris']:
        # !!! Pressed for time, hard-coding PIMCM,re-struct later
        # case sensitive, be careful
        if i['UriType'] == RESTPATH_HB_Dict[hb_type]:
            regex = ".+//(.+)/(.+)$"
            if re.search(regex, i['CallBackUri']):
                match = re.search(regex,i['CallBackUri'])
                hosturl = match.group(1)
                restapi = '/'+match.group(2)
                break
            else:
                print("%s Error Occured with wrong URI format %s" % (HB_Dict[hb_type],  i['CallBackUri']))
                log.error("%s Error Occured with wrong URI format %s" %(HB_Dict[hb_type], i['CallBackUri'])) 
                return None
    c = httplib.HTTPSConnection(host=hosturl,timeout=timeout,context=sslctx) 
    try:
        c.request("PUT", restapi, body, headers)
        res = c.getresponse()
    except Exception, exc:
        log.exception('%s Error With Failed Connection' % HB_Dict[hb_type])
        print exc
        return None
    # Be careful not to return res, it will cause "MaybeEncodingError" exception
    # refer to below link for detail
    # https://stackoverflow.com/questions/21684611/
    return res.status 


