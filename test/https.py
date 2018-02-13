import httplib, urllib
import socket
import ssl
import re

headers = {"Content-type":"application/json", "charset":"UTF-8",\
           "X-Auth-Username":"libo","X-Auth-Password":"libo"}
body='{"VimId": "81f1d9d0-ca13-4eea-a4ce-9bd89a50c9d1"}'

uri = "https://127.0.0.1:1234/pimTokens"
regex = ".+//(.+)/pimTokens"
if re.search(regex, uri):
    match = re.search(regex,uri)
    hosturl = match.group(1)

c = httplib.HTTPSConnection(host=hosturl,\
        timeout=2,context=ssl._create_unverified_context())

try:
    c.request("POST", "/pimTokens",body,headers)
    response = c.getresponse()
except Exception, exc:
    print exc
else:    
    print response.status, response.reason
    data = response.read()
    print data
