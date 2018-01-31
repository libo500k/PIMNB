

from nblib import *


if __name__ == '__main__':
    """
    a = PimAssist.Config()
    print a.getValue('CERT')
    print a.getValue('PASTE')
    """
    a = PimAssist.PimLogger()
    b = PimAssist.PimLogger()

    a.debug('this is debug info')
    a.info('this is information')
    a.warn('this is warning message')
    a.error('this is error message')
    a.fatal('this is fatal message, it is same as logger.critical')
    b.critical('this is critical message') 
