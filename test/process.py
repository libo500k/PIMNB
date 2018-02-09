# multi process example
# run with >python process.py 


import os
from multiprocessing import Pool, TimeoutError
import time
import os
import pdb
import sys
from pprint import pprint
import signal
import datetime

def CtrlC(signum, frame):
    global pool
    print 'You choose to stop me.'
    pool.close()
    pool.join() 
    sys.exit()
 
def say( y,x,index ):
    print  "!!!!!!!!!!!!!!!!!!!!!-----%s--" % index 
    id = os.getpid()
    time.sleep(20)
    t = datetime.datetime.now().isoformat()
    return (id,t,x) 

def cb(x):
    global bb
    bb[x[0]] = x[1]
    pprint(bb)
    pprint(x[2])

if __name__ == '__main__':
    bb = {} 
    signal.signal(signal.SIGINT,CtrlC) 
    print "start main"
    d = {'name':"libo",'password':"p11"}
    pprint(d)
    pool = Pool(3)
    #pdb.set_trace()
    index = 0
    while True:
        for i in range(4):
            # args=(q,) need this format to pass only one varialbe list/tuple/dict  
            res = pool.apply_async(func=say,args = ( [2 , 3 , 4],d,index ),callback = cb) 
            index += 1
            try:
                res.get(timeout=1)
            except TimeoutError:
                print "New task (%s)sent to pool already, waiting for ending, timeout exception" %index
                #print "...%s...." %pool._inqueue
                sys.stdout.flush()
    print "end main"



