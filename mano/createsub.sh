#/bin/bash
source ./token.sh
echo $token


curl -d '{ "NfvoId": "BJ-NFVO-0","Username": "libo","Password": "libo","IdentityUri": "https://127.0.0.1:1234/pimTokens","subType": "pim", "Period": 15, "Heartbeat": 5, "HeartbeatCm": 30, "HeartbeatFm": 30}' -X POST -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  https://127.0.0.1:9141/v1/pimJobs

echo


