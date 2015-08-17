#!/bin/bash

function SJ {
 if (( $(echo "$1 >= $2" | bc -l) )); then
  logit "Local SJ-Hook is latest: $1"
 else
  logit "Github SJ-Hook is newer: $2"
  logit "remove local File"
  cd $hooks_folder
  rm SJ.p*
  logit "downloading new Version"
  wget https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/SJ.py > /dev/null 2>&1
 fi
}

function FileBot {
 if (( $(echo "$1 >= $2" | bc -l) )); then
  logit "Local FileBot-Hook is latest: $1"
 else
  logit "Github FileBot-Hook is newer: $2"
  logit "remove local File"
  cd $hooks_folder
  rm FileBot.p*
  logit "downloading new Version"
  wget https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/FileBot.py > /dev/null 2>&1
 fi
}

function HDAreaOrg {
 if (( $(echo "$1 >= $2" | bc -l) )); then
  logit "Local HDAreaOrg-Hook is latest: $1"
 else
  logit "Github HDAreaOrg-Hook is newer: $2"
  logit "remove local File"
  cd $hooks_folder
  rm HDAreaOrg.p*
  logit "downloading new Version"
  wget https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/HDAreaOrg.py > /dev/null 2>&1
 fi
}

logit(){
   logline=$(date +'%d.%m.%Y')" "$(date +'%H:%M:%S')" pyLoadStuff-Updater\t"
   echo -e "$logline " $* | tee -a $LogFile
   return 0
}

#dont touch

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
pyLoadFolder=${DIR%*/scripts/*}
hooks_folder=$pyLoadFolder/userplugins/hooks
temp_folder=$pyLoadFolder/scripts/pyload_start
LogFile=$pyLoadFolder/Logs/log.txt
cd $temp_folder

##FileBot
if [ -f $hooks_folder/FileBot.py ];then
 wget --no-cache https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/FileBot.py > /dev/null 2>&1
 FB_localversion=$(grep 'version' $hooks_folder/FileBot.py | tr -d '"_version= ')
 FB_githubversion=$(grep 'version' $temp_folder/FileBot.py | tr -d '"_version= ')
 FileBot $FB_localversion $FB_githubversion
 cd $temp_folder
 rm FileBot*
fi

##SJ
if [ -f $hooks_folder/SJ.py ];then
 wget --no-cache https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/SJ.py > /dev/null 2>&1
 SJ_localversion=$(grep 'version' $hooks_folder/SJ.py | tr -d '"_version= ')
 SJ_githubversion=$(grep 'version' $temp_folder/SJ.py | tr -d '"_version= ')
 SJ $SJ_localversion $SJ_githubversion
 cd $temp_folder
 rm SJ.p*
fi

##HDAreaOrg
if [ -f $hooks_folder/HDAreaOrg.py ];then
 wget --no-cache https://raw.githubusercontent.com/Gutz-Pilz/pyLoad-stuff/master/HDAreaOrg.py > /dev/null 2>&1
 HDA_localversion=$(grep 'version' $hooks_folder/HDAreaOrg.py | tr -d '"_version= ')
 HDA_githubversion=$(grep 'version' $temp_folder/HDAreaOrg.py | tr -d '"_version= ')
 HDAreaOrg $HDA_localversion $HDA_githubversion
 cd $temp_folder
 rm HDAreaOrg*
fi
