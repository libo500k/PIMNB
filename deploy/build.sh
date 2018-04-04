#! /bin/bash
#yum install -y rpm-build.x86_64
#pip install virtualenv
virtualenv --no-site-packages pimnb
source pimnb/bin/activate
pip install pyopenssl
pip install paste
pip install webob
pip install PasteDeploy
pip install mysql-python
pip install python-dateutil
pip install psycopg2-binary
pip install simplejson
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



