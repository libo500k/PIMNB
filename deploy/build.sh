#! /bin/bash
#yum install -y rpm-build.x86_64
#pip install virtualenv
virtualenv --no-site-packages pimnb
source pimnb/bin/activate
pip install pyopenssl  --no-cache-dir
pip install paste  --no-cache-dir
pip install webob  --no-cache-dir
pip install PasteDeploy  --no-cache-dir
pip install mysql-python  --no-cache-dir
pip install python-dateutil  --no-cache-dir
pip install psycopg2-binary  --no-cache-dir
pip install simplejson  --no-cache-dir
deactivate
virtualenv --relocatable ./pimnb
cp -r ../cfg/ ../nblib/ ../run.py ../tools/ ./pimnb/

tar cvfz pimnb.tar ./pimnb/
mkdir -p ./{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cp pimnb.tar ./SOURCES/
echo "%_topdir  `pwd`" >~/.rpmmacros
cp pimnb.spec ./SPECS/
rpmbuild -ba ./SPECS/pimnb.spec

#rm -rf BUILD BUILDROOT/ pimnb pimnb.tar RPMS/ SOURCES/ SPECS/ SRPMS/



