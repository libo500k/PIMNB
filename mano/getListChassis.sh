#/bin/bash
source token.sh


a=`curl -X GET -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:9141/v1/pimCm/Chassis?NfvoId=BJ-NFVO-0&qType=pim'`

echo $a

a=`curl -X GET -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:9141/v1/pimCm/Chassis/4C839712E4C311E690AE0894EF36130A?NfvoId=BJ-NFVO-0&qType=pim'`

echo $a


