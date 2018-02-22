# this script can ONLY be run on the controller node, 
# the token is NOT authorized for some reason if running on the nodes outside of OpenStack
# the reason maybe the openstack keystone bind to the localhost, 
# change to external IP will failed even on the controller node, !!!no response body!!!

ip="10.100.46.45"
curl -i \
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
  "http://localhost:5000/v3/auth/tokens" ; echo
