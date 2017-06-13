#!/bin/bash

# Run command $1. On error write message $2
function runCommand {
    echo "Running command ${1}";
    $1 &> /dev/null;
    [ $? -ne 0 ] && echo "Error: " "${2}";
}

# Install packages listed in $@
function installPackage {
    echo "Installing packages $@";
    for i in $@;
    do
        runCommand "dnf install -y ${i}" "install ${i}";
    done;
}

installPackage fish nc tmux bind unbound bind-utils rng-tools
runCommand 'rngd -r /dev/urandom' 'Entropy sources'
echo 'OPTIONS="-d 5"' >> /etc/sysconfig/named
echo 1 > /proc/sys/net/ipv4/ip_forward
pushd /vagrant/python
runCommand './setup.py install' 'Install python framework'
popd 
runCommand 'dnssec-testing-setup' 'Set up DNS servers and resolvers' 
dnssec-testing-test-unsecure

exit 0
