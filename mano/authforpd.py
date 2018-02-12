#/bin/bash

a=`curl -X POST -H 'Content-Type:application/json' -H 'charset:UTF-8' -H 'X-Auth-Token: Token1234'  -v -k  https://127.0.0.1:1234/pimTokens`

echo $a


