from OpenSSL.crypto import PKey
from OpenSSL.crypto import TYPE_RSA, FILETYPE_PEM
from OpenSSL.crypto import dump_privatekey, dump_publickey


pk = PKey()
print(pk)
pk.generate_key(TYPE_RSA, 1)
dpub = dump_publickey(FILETYPE_PEM, pk)
print(dpub)
dpri = dump_privatekey(FILETYPE_PEM, pk)
print(dpri)
