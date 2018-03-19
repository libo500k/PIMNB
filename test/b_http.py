import httplib, urllib
import socket
import ssl
import re
import pdb
import base64

auth = base64.b64encode('USERID'+ ':'+ 'Passw0rd') 

headers = {"Content-type":"application/json", "charset":"UTF-8",\
           "Authorization": "Basic "+ auth}
#body='{"VimId": "81f1d9d0-ca13-4eea-a4ce-9bd89a50c9d1"}'

#uri = "https://10.240.197.157/v1/pimCm"
#regex = ".+//(.+)/v1/pimTokens"
pdb.set_trace()
hosturl = "10.240.197.157:443"
#if re.search(regex, uri):
#    match = re.search(regex,uri)
#    hosturl = match.group(1)
c = httplib.HTTPSConnection(host=hosturl,\
        timeout=2,context=ssl._create_unverified_context())

try:
    c.request("GET", "/v1/pimCm",None,headers)
    response = c.getresponse()
except Exception, exc:
    print exc
else:    
    print response.status, response.reason
    data = response.read()
    print data
