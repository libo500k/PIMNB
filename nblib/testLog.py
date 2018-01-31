
import PimLogger as a

if __name__ == '__main__':
    """
    a = PimAssist.Config()
    print a.getValue('CERT')
    print a.getValue('PASTE')
    """

    a.debug('this is debug info')
    a.info('this is info message')
    a.error('this is error message')

    try:
        1/0
    except(ZeroDivisionError):
        a.exception('this is an exception')
    else:  
        print "not exception"  
    """  
    try:
        a.info("aaaaaaaaaaaaaa")
        1/0
    except(TypeError):
        a.exception('this is a type error ')
    else:
        print "not exception"
    """ 
    print "continue"



