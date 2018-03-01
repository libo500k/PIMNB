#!/user/bin/env python

"""
PimPool.py
   : Process Pool Class for NFV PIM northbound
"""
__author__     = "Li Bo"
__copyright__  = "Copyright 2018, Lenovo Research"


from multiprocessing import Pool
from multiprocessing import TimeoutError
import logging
import PimAssist
import signal
import PimList
import PimAgent

class PimPool(object):
    _instance = None
    def __new__(cls,*args,**kw):
        if not cls._instance:
            poolsize = PimAssist.Config().getValue('POOL_SIZE')
            original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            cls._instance = Pool(int(poolsize))
            signal.signal(signal.SIGINT, original_sigint_handler)
        return cls._instance

    @classmethod
    def getInstance(cls):
        if not cls._instance:
           PimPool()
        return cls._instance 
def touch():
    PimPool.getInstance()

def close():
    PimPool.getInstance().close()

def terminate():
    PimPool.getInstance().terminate()

def join():
    PimPool.getInstance().join()

def apply_async(**args):
    return PimPool.getInstance().apply_async(**args)




