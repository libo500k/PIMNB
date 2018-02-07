import MySQLdb

db = MySQLdb.connect("localhost","root","root","PIMNB")
ip = "10.20.1.1"
nfvoid = "mano123"
hb=20
pe=10
user="libo"
p="libo"
url="uri"

cursor = db.cursor()
sql = "INSERT INTO RegMano(ip,nfvoid,heartbeat,period,identityuri,user,passwd)\
VALUES ('%s','%s',%s,%s,'%s','%s','%s')" % (ip,nfvoid,hb,pe,url,user,p)

#sql = "INSERT INTO RegMano(IP,nfvoid,heartbeat,period,identityuri,user,passwd)\
#       VALUES ('10.20.1.1','aaa', 20,10, 'M', 'libo','libo')"
print (sql)
try:
    cursor.execute(sql)
    db.commit()
except:
    print "--------------------"
    db.rollback()
finally:
    db.close()

