
ip="10.100.46.45"

rev=`curl  -s -i \
  -H "Content-Type: application/json" \
  -d '
{ "auth": {
    "identity": {
      "methods": ["password"],
      "password": {
        "user": {
          "name": "admin",
          "domain": { "id": "default" },
          "password": "admin"
        }
      }
    }
  }
}' \
  "http://${ip}:5000/v3/auth/tokens" `; 

token=`echo ${rev}|grep X-Subject-Token|awk -F ':' '{print $2}'`


echo ${token}
