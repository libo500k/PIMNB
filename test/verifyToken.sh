# remember to change the token in case expired

token="gAAAAABajoe1LxrQcjSRHpA3sL9dt-W_l9LU8r2YlglISgPn11A8oLWbPwQYiekCFaaKuI8NzI08x9leWykSGAX83h9_3EKnqqfGrjhCAZTgKqQ4DeRQaepH4QFK2j5W_M6QgcGLjJDJDp2eu1wQO4IP9hOj7GPGKA"
auth_url="http://10.100.46.45:5000/v2.0/tenants"

echo ${token}

curl  -v -H "X-Auth-Token:${token} " ${auth_url} 

echo
