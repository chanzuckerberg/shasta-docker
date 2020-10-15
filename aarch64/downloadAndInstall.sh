#!/bin/bash

TAGS=$(curl -s https://api.github.com/repos/chanzuckerberg/shasta/releases | grep -oP '"tag_name": "\K(.*)(?=")')
echo "Found release tags: $TAGS".
for TAG in $TAGS
do
    if [[ "$TAG" > "0.5.1" ]]; then
   	EXECUTABLE="shasta-Linux-ARM-$TAG"
    	curl -O -L https://github.com/chanzuckerberg/shasta/releases/download/$TAG/$EXECUTABLE
    	chmod ugo+x $EXECUTABLE
    	echo "Done downloading $EXECUTABLE."    
    fi
done

echo "Installing Pre-requisites."
curl -O -L https://raw.githubusercontent.com/chanzuckerberg/shasta/master/scripts/InstallPrerequisites-Ubuntu.sh
chmod ugo+x InstallPrerequisites-Ubuntu.sh
./InstallPrerequisites-Ubuntu.sh --minimal

apt-get clean
apt-get purge
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
