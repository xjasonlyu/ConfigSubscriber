#!/bin/sh

# generate random hex string
cat /dev/urandom | head -c 1024 | md5sum | awk '{print$1}'
