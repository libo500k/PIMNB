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
                rundata[key]['cmstamp'] = str(c) 
                print ("ooo---000 send request--000");
                changed = True
            else:
                stamp = PimOps.getDateTimeFromISO8601String(rundata[key]['cmstamp']).replace(tzinfo=None)
                delta = datetime.timedelta(seconds = rundata[key]['basic']['Heartbeat'])
                if  c >= stamp+delta :
                    rundata[key]['cmstamp'] = str(c)
                    print ("ooo---111 send request--111");
                    changed = True

        if changed == True :
            PimOps.globalDict.merge(rundata)
        time.sleep(interval)
