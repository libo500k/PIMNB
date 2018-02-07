#/bin/bash

a=`curl -d '{ "NfvoId": "BJ-NFVO-1","Username": "libo","Password": "libo","IdentityUri": "https://192.168.112.100/tokens","subType": "pim", "Period": 15, "Heartbeat": 30}' -X POST -H 'Content-Type:application/json' -H 'charset:UTF-8' -H 'X-Auth-Token: Token1234'  -v -k  https://127.0.0.1:8080/v1/pimJobs`

echo $a


