# remember to change the token in case expired


token="gAAAAABaj7XwUZnjunA1lgegbqrfY4nDneaBUi31u6kWG6ZMWRk1YVHmLmKd9a9uyMg91a3GL6DkSWh8nHUIUgE5TGH7eAJgSYoLCiuucRn83Pbw2pUQlXJ2u-y3MDpJNmeBtadAVwRGV5ds8NXi3uj8t4f7RHn0Og"
auth_url="http://10.100.46.45:5000/v2.0/tenants"

echo ${token}

curl  -v -H "X-Auth-Token:${token} " ${auth_url} 

echo
