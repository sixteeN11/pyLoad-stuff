#!/bin/bash

## Log
DATE=$(date +%d.%m.%Y\ %H:%M:%S)
logline=$(date +'%d.%m.%Y')" "$(date +'%H:%M:%S')" FileBot"
LogFile=/root/.pyload/Logs/log.txt
## DTS2AC3 um den Datentransfer von OSDrive zu NASDrive zu umgehen (NASHD -> NASHD)
##tmpFolder=$MediaDir/tmp

## String Manipulation
mailtitle_ext=${1##*/}
mailtitle=${mailtitle_ext%.*}
pfad_00=${1%/*.mkv}
pfad=${pfad_00##*/Medien}
if grep -q ".mkv" "$1"; then
        echo  "$logline ##########################" | tee -a $LogFile
        echo  "$logline Dateihandling nachdem FILEBOT fertig ist" | tee -a $LogFile
        echo  "$logline Datei wurde nach ~${1%/*.mkv}/* verschoben" | tee -a $LogFile
        DUCMD="$(which \du) -m"
        FileSize1=$($DUCMD "$1" | cut -f1)
        cd /

        echo "$logline Neues Erstelldatum" | tee -a $LogFile
        touch -c "$1"

        echo "$logline CHMOD 777" | tee -a $LogFile
        chmod 777 "$1"
        Final=$($DUCMD "$1" | cut -f1)
        Final2=$(echo "$Final" | sed -e :a -e 's/\(.*[0-9]\)\([0-9]\{3\}\)/\1.\2/;ta')

        echo "$logline E-Mail senden" | tee -a $LogFile
        echo -e "Verschoben nach:\t ~/NAS_HD$pfad/\n\nGroesse:\t$Final2 MB\n\n\nSincerly\nyour lovely NAS" | mailx -s "INFO: $mailtitle runtergeladen" hfdgdg7@gmail.com;

        echo "$logline Lösche leere Ordner" | tee -a $LogFile
        cd /root/.pyload/Downloads
        find . -type d -empty -exec rmdir {} \;
fi
