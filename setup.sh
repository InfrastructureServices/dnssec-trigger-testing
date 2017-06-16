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

# Install necessary packages
installPackage fish nc tmux bind unbound bind-utils rng-tools git clang clang-analyzer libcmocka-devel
# We are going to generate a lot of key pairs
runCommand 'rngd -r /dev/urandom' 'Entropy sources'
# Set global debug option for bind
echo 'OPTIONS="-d 5"' >> /etc/sysconfig/named
# Allow IP forwarding between network namespaces
echo 1 > /proc/sys/net/ipv4/ip_forward
# Install python framework for dnssec testing
pushd /vagrant/python
runCommand './setup.py install' 'Install python framework'
popd 
# Set up DNS Servers for testing purposes
runCommand 'dnssec-testing-setup' 'Set up DNS servers and resolvers' 
# Check that the resolver works
dnssec-testing-test-unsecure
dig +dnssec @100.99.1.2 example.com

# Clone dnssec-trigger repository and build from sources
mkdir /dnssec
pushd /dnssec
runCommand 'git clone https://github.com/msehnout/dnssec-trigger-fedora.git .' 'Clone dnssec-trigger repository into local dir'
runCommand 'dnf builddep dnssec-trigger.spec -y' 'Install dependencies'
runCommand './configure --with-forward-zones-support --with-hooks=networkmanager' 'Configure'
# Run unit testing
make test
popd

exit 0
