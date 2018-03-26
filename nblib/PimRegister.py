#!/user/bin/env python

"""
PimRegister.py
   : Register event monitor class for NFV PIM northbound
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
import PimAssist
import json
import base64 


"""
    Global event severity list
"""
LXCA_EVENT_SEVERITY_LIST = {
"fatal",
"critical",
"major",
"warning",
"minor",
"informational"
}


"""
    Global event type list
"""
LXCA_EVENT_TYPE_LIST = {
"all",
"cooling",
"power",
"disks",
"memory",
"processors",
"system",
"adaptor",
"expansion",
"iomodule",
"blade",
"switch",
"audit"
}


"""
    data structure of event monitor in LXCA
"""
class lxca_event_monitor:
    
    def __init__(self):
        self.name = ''
        self.ip = ''
        self.port = 8080
        self.protocol = 'rest'
        self.description = 'forward events to PIM'
        self.enable = "true"
        self.requestTimeout = 30
        self.ignoreExcluded = 'false'
        self.restProtocol = 'HTTP'
        self.restPath = ''
        self.restMethod = 'POST'
        self.restAuthentication = 'NONE'
        # eventFilter will build dynamically
        self.eventFilter=''
        self.matchEverything = 'true'
        self.scheduler = {"events":[],"enabled":"false","showSummary":"false"}


"""
    register a event monitor in LXCA for PushAlarm
"""
def registerMonitor(ip, port, restPath):

    # get username/passwd/ip_addr of LXCA from cfg.ini
    username = PimAssist.Config().getValue('PIM_USER')
    password = PimAssist.Config().getValue('PIM_PASS')
    pimIP = PimAssist.Config().getValue('PIM_IP')
    method = 'POST'
    em_url = '/events/monitors'
    lxca_url = 'https://%s%s' % (pimIP, em_url)

    try: 
        # set CERT_NONE 
        context = ssl._create_unverified_context()
        conn = httplib.HTTPSConnection(pimIP, context=context)

        # build authorization for LXCA
        user_and_pass = base64.b64encode(username + ':' + password)
        headers = {"Authorization": "Basic %s" % user_and_pass,"Content-type":"application/json", "charset":"UTF-8"}

        # fill event monitor for PushAlarm
        em = lxca_event_monitor()
        em.name = 'hehe PIM event monitor'
        em.ip = '%s' % ip
        em.port = port
        em.description = 'forward events to PIM'
        em.restPath = restPath

        severity_type_list=[]
        for s in LXCA_EVENT_SEVERITY_LIST:
            for t in LXCA_EVENT_TYPE_LIST:
                item = '{"severity":"%s", "type":"%s"}' % (s, t)
                severity_type_list.append(item)
        

        # convert severity_type_list to string
        string = '['
        for i in severity_type_list:
            if i is not severity_type_list[-1]:
                string = string + i + ','
            else:
                string = string +i
        string = string + ']'


        # eventFilter is a string
        em.eventFilter = '{"filter":{"componentIDs":["FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF","4C839712E4C311E690AE0894EF36130A"], "sourceIDs":["FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF","4C839712E4C311E690AE0894EF36130A"], "typeSeverity":%s, "categories":["GENERAL"]}}' % string
        # print em.eventFilter

        body = '{"name":"%s", "ipAddress":"%s", "port": %s, "protocol":"%s", "description":"%s", "enable":"%s", "requestTimeout":%s, "ignoreExcluded":%s, "restProtocol":"%s", "restPath":"%s", "restMethod":"%s", "restAuthentication":"%s", "eventFilter":' % (em.name, em.ip, em.port, em.protocol, em.description, em.enable, em.requestTimeout, em.ignoreExcluded, em.restProtocol, em.restPath, em.restMethod, em.restAuthentication )
        body += em.eventFilter
        #body += '"matchEverything":%s, "scheduler":{%s}}' % (em.matchEverything, em.scheduler)
        body += ', "matchEverything":%s, "scheduler":{"events":[], "enabled":false, "showSummary":false}}' % em.matchEverything

        #print 'lxca_url', lxca_url
        #print 'method', method
        #print 'headers', headers
        # print 'body', body

        conn.request(method, lxca_url, body=body, headers=headers)

        pimres = conn.getresponse()
        conn.close()

        # 200 stands for OK
        if pimres.status == 200:
            return True
        else:
            # when error, print out details
            print "pimres.status", pimres.status
            msg = pimres.msg
            print "error msg", pimres.status, msg.__dict__, 
            return False

    except (httplib.HTTPException, socket.timeout, socket.gaierror, Exception), e:
        log.error('%s is unreachable, Exception %s %s' % (lxca_url, e.__class__.__name__, e))
        print 'lxca_url %s is unreachable, Exception %s %s' % (lxca_url.encode('utf-8'), e.__class__.__name__, e)
        print "pimres.status", pimres.status, pimres.__dict__, pimres.msg.__dict__

    return False
