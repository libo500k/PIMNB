#!/user/bin/env python

"""
Assist.py
   : assistant class for NFV PIM northbound
"""
__author__     = "Li Bo"
__copyright__  = "Copyright 2018, Lenovo Research"


from ConfigParser import SafeConfigParser

class Config(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.read('./cfg/cfg.ini')
	return

    def getValue (self,key):
	return self.parser.get('DEFAULT',key)	



