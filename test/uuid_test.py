import uuid
import pdb

name = 'http://10.100.46.45/auth/v2.0'
namespace = b'xclarity'

print uuid.uuid1()
print uuid.uuid3(uuid.NAMESPACE_DNS,name)
print uuid.uuid4()

pdb.set_trace()
u =  uuid.uuid5(uuid.NAMESPACE_URL,name)
