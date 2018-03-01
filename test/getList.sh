#/bin/bash
#source token.sh

token = "122"

a=`curl -X GET -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'http://127.0.0.1:2345/v1/pimCm?NfvoId=BJ-NFVO-0&qType=pim'`

echo $a


