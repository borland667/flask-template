#!/bin/sh

CI_PROJECT_DIR=`pwd`
PATH=$PATH:$CI_PROJECT_DIR/src/sbin

set | grep CI | grep -v grep

# Specific internal runners check
# (to avoid errors when runners are different)
HOSTNAME_TAG="unx"
RUNNER_CHECK=`uname -n | grep ${HOSTNAME_TAG} | wc -l`

if [[ ${RUNNER_CHECK} -eq 1 ]]; then
	printf "Internal runner detected!\n"
else

	#
	# Installing package dependencies
	#
	printf " o Installing package dependencies...\n"
	# RHEL only
	yum install rpm-build -y

fi
