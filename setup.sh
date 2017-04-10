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

installPackage fish nc tmux bind unbound

exit 0
