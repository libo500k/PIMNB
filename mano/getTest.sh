#/bin/bash

token="aaaatokena"

a=`curl -X GET -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:9141/v1/pimCm/test?NfvoId=BJ-NFVO-0&qType=pim'`

echo $a


