#/bin/bash

a=`curl -d '{ "NfvoId": "BJ-NFVO-0","Username": "libo","Password": "libo","IdentityUri": "https://127.0.0.1:1234/pimTokens","subType": "pim", "Period": 15, "Heartbeat": 30}' -X POST -H 'Content-Type:application/json' -H 'charset:UTF-8' -H 'X-Auth-Token: Token1234'  -v -k  https://127.0.0.1:9141/v1/pimJobs`

echo $a


