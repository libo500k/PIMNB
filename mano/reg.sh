#/bin/bash
source token.sh

a=`curl -X PUT -H 'Content-Type:application/json' -H 'charset:UTF-8' -H "X-Auth-Token: ${token}"  -v -k  'https://127.0.0.1:1234/pimJobs'`

echo $a


