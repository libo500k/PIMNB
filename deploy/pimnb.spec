Name:           pimnb
Version:        1.0
Release:        1%{?dist}
Summary:        pim norht bound agent

Group:          Lenovo
License:        GPLv2+
URL:            www.lenovo.com
Source:         ../pimnb.tar

%description
%install
install -m 755 -d %{buildroot}/PIMNB
echo `pwd`
cp -a -r  ../pimnb.tar  %{buildroot}/PIMNB

%files
/PIMNB/pimnb.tar

%defattr(0755,root,root,-)
%post
echo ">>> Unpackage Target <<<"
cd /PIMNB
tar xvfz pimnb.tar > /tmp/pimnb.txt

%postun
rm -rf /PIMNB
                 
