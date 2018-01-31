#!/user/bin/env python

"""
PimLogger.py
   : Log Class for NFV PIM northbound
"""
__author__     = "Li Bo"
__copyright__  = "Copyright 2018, Lenovo Research"


import logging
import PimAssist

class PimLogger(object):
    _instance = None
    def __new__(cls,*args,**kw):
        if not cls._instance:
            cls._instance = logging.getLogger();
            formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
            log_path = PimAssist.Config().getValue('Log')
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            # console_handler = logging.StreamHandler(sys.stdout)
            # console_handler.formatter = formatter
            cls._instance.addHandler(file_handler)
            # cls._instance.addHandler(console_handler)
            cls._instance.setLevel(logging.DEBUG)
        return cls._instance

    @classmethod
    def getInstance(cls):
        if not cls._instance:
           PimLogger()
        return cls._instance 


def debug(m):
     PimLogger.getInstance().debug(m)


def info(m):
    PimLogger.getInstance().info(m)

def error(m):
    PimLogger.getInstance().error(m)

def exception(m):
    PimLogger.getInstance().exception(m)


