#/bin/bash

a=`curl -X DELETE  -H 'Content-Type:application/json' -H 'charset:UTF-8' -H 'X-Auth-Token: Token1234'  -v -k  https://127.0.0.1:8080/v1/pimJobs/BJ-NFVO-1?subType=pim`

echo $a


