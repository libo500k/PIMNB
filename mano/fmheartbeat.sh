#/bin/bash
source token.sh

a=`curl -d '"Version": "1.0","VimId": "81f1d9d0-ca13-4eea-a4ce-9bd89a50c9d1","SrcType": "vpim","MsgType": "pimFmHeartbeat"'-X PUT -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:1234/pimFm'`

echo $a


