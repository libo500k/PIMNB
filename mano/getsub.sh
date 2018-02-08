#/bin/bash

a=`curl -X GET -H 'Content-Type:application/json' -H 'charset:UTF-8' -H 'X-Auth-Token: Token1234'  -v -k  'https://127.0.0.1:8080/v1/pimJobs?NfvoId=BJ-NFVO-1&qType=pim'`

echo $a


