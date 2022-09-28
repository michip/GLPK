#!/bin/bash

# Download and extract Netlib testset in .SIF format
wget ftp://ftp.numerical.rl.ac.uk/pub/cuter/netlib.tar.gz
gunzip netlib.tar.gz
tar -xf netlib.tar

# Remove non-instance files
rm netlib/netlib.html
rm netlib/NETLIB.dat
rm netlib/README
rm netlib.tar