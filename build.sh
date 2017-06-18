#!/bin/sh

CI_PROJECT_DIR=`pwd`
PATH=$PATH:$CI_PROJECT_DIR/src/sbin

set | grep CI | grep -v grep

#
# Inserting Version
#
printf " o Inserting Version...\n"

for f in \
    src \
    build/SOURCES
do
    printf "  - Processing $f\n"
    sed -i "s/%%VERSION%%/$CI_BUILD_TAG/" $f > build.log 2>&1
done

#
# Building
#

printf " o Building...\n"
cd $CI_PROJECT_DIR/build

printf "  - Tarring sources..."
(cd $CI_PROJECT_DIR/src && tar -cf - *) | tar -C SOURCES -xf - >> build.log 2>&1
if [ $? -ne 0 ]; then
    printf "Failed\n"
    cat build.log
    exit 1
fi
printf "done\n"


printf " - Generating changelog..."
$CI_PROJECT_DIR/build/SOURCES/genchangelog >> SPECS/scripts-restify.spec
if [ $? -ne 0 clear
 then
    printf "Failed\n"
    cat build.log
    exit 1
fi
printf "done\n"

printf "  - Building RPM..."
rpmbuild \
    --define '__os_install_post /usr/lib/rpm/redhat/brp-compress %{nil}' \
    --define "%_topdir $CI_PROJECT_DIR/build" \
    --define "_ci_build $CI_BUILD_ID" \
    --define "_version $CI_BUILD_TAG" \
    --define "_binary_payload w9.gzdio" \
    --define "_binary_filedigest_algorithm 1" \
    --define "_version $CI_BUILD_TAG" \
    --define "__os_install_post \
        /usr/lib/rpm/redhat/brp-compress \
        %{!?__debug_package:/usr/lib/rpm/redhat/brp-strip \
        %{__strip}} /usr/lib/rpm/redhat/brp-strip-static-archive \
        %{__strip} /usr/lib/rpm/redhat/brp-strip-comment-note \
        %{__strip} %{__objdump} /usr/lib/rpm/brp-python-bytecompile \
        /usr/lib/rpm/redhat/brp-java-repack-jars %{nil}" \
    -bb SPECS/scripts-restify.spec >> build.log 2>&1

if [ $? -ne 0 ]; then
    printf "Failed\n"
    cat build.log
    exit 1
fi

RPM=`ls -1 $CI_PROJECT_DIR/build/RPMS/x86_64/`
if [ "x${RPM}" == "x" ]; then
    printf "failed\n"
else
    printf "done\n"
fi

printf " - Discovering runner..."

# Specific internal runners check
# (to avoid errors when runners are different)
HOSTNAME_TAG="unx"
RUNNER_CHECK=`uname -n | grep ${HOSTNAME_TAG} | wc -l`

if [[ ${RUNNER_CHECK} -eq 1 ]]; then
    printf "Internal runner detected!\n"

    #
    # Deploy
    #

    printf " o Uploading packages...\n"
    printf "  - Copying RPMs to Yum Repos..."
    for repo in caslias01.telecom.tcnz.net:yum/rhel7/ iaas-lab:
    do
        scp -o StrictHostKeyChecking=no -qpr RPMS/* yum@$repo >> build.log 2>&1
        if [ $? -ne 0 ]; then
            printf "Failed\n"
            cat build.log
            exit 1
        fi
    done

    printf "done\n  - Regenerating Yum Repo cache..."
    for repo in caslias01.telecom.tcnz.net:yum/rhel7 iaas-lab:.
    do
        SVR=`echo $repo | awk -F: '{print $1}'`
        YUM_PATH=`echo $repo | awk -F: '{print $2}'`
        ssh -q yum@${SVR} "createrepo --update $YUM_PATH" >> build.log 2>&1
        if [ $? -ne 0 ]; then
            printf "Failed\n"
            cat build.log
        exit 1
        fi
    printf "done\n"
    done
else
    printf "Non-internal runner detected!"
    printf "\nDeploy disabled!"
fi

