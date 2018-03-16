import cPickle
import httplib, urllib
import pdb


c = httplib.HTTPConnection(host="127.0.0.1:2345",timeout=1)
headers = {"Content-type":"application/json", "charset":"UTF-8",\
               "X-Auth-Token": "aaaa"}
c.request("GET", "/v1/pimCm", None, headers)

res = c.getresponse()
print res.status
#print res.read()


binary = cPickle.dumps(res.read(),2)
pdb.set_trace()
print binary
