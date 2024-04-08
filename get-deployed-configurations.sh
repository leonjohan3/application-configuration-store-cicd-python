#!/bin/bash
set -ue -o pipefail

if [ $# -lt 1 ] ; then
    echo "Usage: $0 root_folder_of_the_application_configuration_store"
    exit 1
fi

if [ ! -d $1 ] ; then
    echo "ERROR, $1 should be root folder of the application configuration store"
    exit 1
fi

TEMP_FOLDER=$(mktemp -d "${TMPDIR:-/tmp}/$(basename $0).XXXXXXXXXXXX")
readonly ROOT_FOLDER=$1
readonly ACS_PREFIX=acs

for DI in $(ls $ROOT_FOLDER) ; do

    if [ -d $ROOT_FOLDER/$DI ] ; then
        echo $DI
        mkdir $TEMP_FOLDER/$DI

        for EV in $(ls $ROOT_FOLDER/$DI) ; do
            echo $EV
            mkdir $TEMP_FOLDER/$DI/$EV
            aws appconfigdata start-configuration-session --application-identifier "$ACS_PREFIX/$DI" --environment-identifier "$EV" --configuration-profile-identifier "$EV" --output text > $TEMP_FOLDER/session
            SESSION=$(<$TEMP_FOLDER/session)
            aws appconfigdata get-latest-configuration --configuration-token "$SESSION" $TEMP_FOLDER/$DI/$EV/application.yaml > /dev/null
            #break
        done
        
        #break
    fi
done


# for DI in * ; do if [ -d $DI ] ; then for FI in $(ls $DI) ; do diff  $DI/$FI/application.yaml ~/tmp/get-deployed-configurations.sh.jcALJeFoBezE/$DI/$FI ; done ; fi ; done
