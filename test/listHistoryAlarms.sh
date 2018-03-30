token="gAAAAABaj7XwUZnjunA1lgegbqrfY4nDneaBUi31u6kWG6ZMWRk1YVHmLmKd9a9uyMg91a3GL6DkSWh8nHUIUgE5TGH7eAJgSYoLCiuucRn83Pbw2pUQlXJ2u-y3MDpJNmeBtadAVwRGV5ds8NXi3uj8t4f7RHn0Og"
echo ${token}

echo "curl -v -H "X-Auth-Token:${token}" -k https://127.0.0.1:9141/v1/pimFm/hisAlarms"
curl -i -v -H "X-Auth-Token:${token}" -k https://127.0.0.1:9141/v1/pimFm/hisAlarms
