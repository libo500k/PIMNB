import datetime
import dateutil.parser
import pdb

def getDateTimeFromISO8601String(s):
    d = dateutil.parser.parse(s)
    return d


if __name__ == '__main__':
    # t = datetime.datetime.now().isoformat()
    # s = getDateTimeFromISO8601String(t) 

    t = "2016-05-30T00:00:00.000Z"
    s = getDateTimeFromISO8601String(t)
    #s = s.replace(tzinfo=pytz.timezone('UTC'))
    s =  s.replace(tzinfo=None)
    t1 = datetime.datetime.now().isoformat()
    s1 = getDateTimeFromISO8601String(t1)
    #s1 = s1.replace(tzinfo=pytz.timezone('UTC'))
    s1.replace(tzinfo=None)
    s2 = s1 - s
    if s1 > s:
        v = True
    else:
        v = False
    pdb.set_trace()
    print "---------------------------------------------"


