Name:       scripts-restify
Version:    %{_version}
Release:    %{_ci_build}
Summary:    IaaS Orchestration Tool Linux Scripts Runner REST Interface
Group:      Infrastructure/Automation
License:    Proprietary
URL:        http://gitlab.telecom.tcnz.net/iaas/scripts-restify
Requires:   openssl, nginx, supervisor, postgresql, postgresql-server, postgresql-devel, python-virtualenv, python-pip, python-devel, gcc, openssl-devel, readline-devel, bzip2-devel, sqlite-devel
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
AutoReqProv:    no

%description
Scripts restify is a rest backend service for running linux scripts powered by flask.


%prep


%build


%install
test -d %{buildroot}/appl/restify/web || mkdir -p %{buildroot}/appl/restify/web
test -d %{buildroot}/appl/restify/bin || mkdir -p %{buildroot}/appl/restify/bin
test -d %{buildroot}/var/log/appl/restify || mkdir -p %{buildroot}/var/log/appl/restify
test -d %{buildroot}/appl/restify/web/logs || mkdir -p %{buildroot}/appl/restify/web/logs
test -d %{buildroot}/appl/restify/etc || mkdir -p %{buildroot}/appl/restify/etc
test -d %{buildroot}/etc/supervisor.d/ ||  mkdir -p %{buildroot}/etc/supervisor.d/
test -d %{buildroot}/etc/nginx/conf.d || mkdir -p %{buildroot}/etc/nginx/conf.d

cd %{buildroot}/appl/restify/web
(cd %{_sourcedir} && tar -cf - .) | tar -xvf -

rm -f %{buildroot}/appl/restify/web/genchangelog
rm -f %{buildroot}/appl/restify/web/nginx.conf
rm -f %{buildroot}/appl/restify/web/gunicorn_config.py
rm -f %{buildroot}/appl/restify/web/supervisor.conf
rm -f %{buildroot}/appl/restify/web/create_venv.sh

install -m 0664 %{_sourcedir}/nginx.conf %{buildroot}/etc/nginx/conf.d/restify.conf
install -m 0664 %{_sourcedir}/create_venv.sh %{buildroot}/appl/restify/bin/create_venv.sh
install -m 0755 %{_sourcedir}/supervisor.conf %{buildroot}/etc/supervisor.d/restify.ini
install -m 0755 %{_sourcedir}/gunicorn_config.py %{buildroot}/appl/restify/etc/gunicorn_config.py

%pre
getent group restify >/dev/null || groupadd -f -r restify
if ! getent passwd restify >/dev/null ; then
        useradd -r -m -g restify -d /appl/restify -s /bin/bash -c "Scripts Restify Application Account" restify > /dev/null 2>&1
    else
        useradd -r -m -g restify -d /appl/restify -s /bin/bash -c "Scripts Restify Application Account" restify > /dev/null 2>&1
    fi
    cp -f /etc/skel/.bashrc /appl/restify/
    cp -f /etc/skel/.bash_profile /appl/restify
    chown restify:restify /appl/restify -R
else
    usermod -g restify -d /appl/restify -s /bin/bash -c "Scripts Restify Application Account" -m restify > /dev/null 2>&1

    if [[ ! -r /etc/skel/.bashrc ]]; then
        cp -f /etc/skel/.bashrc /appl/restify/
    fi

    if [[ ! -r /etc/skel/.bash_profile ]]; then
        cp -f /etc/skel/.bash_profile /appl/restify/
    fi

    chown restify:restify /appl/restify -R
fi

%post
test -d /var/log/appl/restify || mkdir -p /var/log/appl/restify
chown restify:restify /var/log/appl/restify -R
cat /appl/restify/.bash_profile | grep -v "unalias ls" > appl/restify/.bash_profiletmp
mv -f appl/restify/.bash_profiletmp appl/restify/.bash_profile

# Check SSL certificate files
if [[ ! -r /etc/pki/tls/certs/restify.telecom.tcnz.net.crt ]]; then
    echo "Remember to update the restify.telecom.tcnz.net.crt file!"
    cat /etc/ssl/certs/localhost.crt > /etc/ssl/certs/restify.telecom.tcnz.net.crt
fi

if [[ ! -r /etc/pki/tls/private/restify.telecom.tcnz.net.key ]]; then
    echo "Remember to update the restify.telecom.tcnz.net.key file!"
    cat /etc/pki/tls/private/localhost.key > /etc/pki/tls/private/restify.telecom.tcnz.net.key
fi

if [[ ! -r /etc/pki/CA/certs/spark-ca.crt ]]; then
    echo "Remember to update the spark-ca.crt file!"
    cat /etc/pki/tls/certs/ca-bundle.crt > /etc/pki/CA/certs/spark-ca.crt
fi

if [[ -r /etc/nginx/conf.d/default.conf ]]; then
    mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.disabled
fi

# Enforce group for nginx to serve static files properly
chgrp nginx /appl/restify
chmod 770 /appl/restify

if [[ ! -d /appl/restify/venv ]]; then
    echo "Remember to install the python dependencies via pip (one-off)"
    echo
    echo "set your http and https proxy variables."
    echo
    echo "virtualenv /appl/restify/venv"
    echo "venv/bin/pip install -r web/requirements.txt"
fi

systemctl daemon-reload

SERVICES="restify nginx mongod"

for SVC in $SERVICES;
do
    # RHEL7 style systemd
    systemctl restart ${SVC}
    sleep 2
    systemctl enable ${SVC}
done

%preun


%postun


%clean
rm -rf %{buildroot}


%files
%defattr(-,restify,restify,-)
%attr(-, restify, nginx) /appl/restify/web
%attr(0755, restify, restify) /appl/restify/bin
%attr(0644, root, root) /etc/supervisor.d/restify.ini
%attr(0644, nginx, restify) /etc/nginx/conf.d/restify.conf
%config(noreplace) /etc/nginx/conf.d/restify.conf
%config(noreplace) /etc/supervisor.d/restify.ini
%config(noreplace) /appl/restify/etc/gunicorn_config.py
%config(noreplace) /appl/restify/web/settings.py


%changelog

