#!/bin/bash

## Log
DATE=$(date +%d.%m.%Y\ %H:%M:%S)
logline=$(date +'%d.%m.%Y')" "$(date +'%H:%M:%S')" FileBot"
LogFile=/root/.pyload/Logs/log.txt

## String Manipulation
mailtitle_ext=${1##*/}
mailtitle=${mailtitle_ext%.*}
pfad_00=${1%/*.mkv}
pfad=${pfad_00##*/Medien}

if grep -q ".mkv" "$1"; then
        ## Schreib was in den pyLoad Log
        echo  "$logline ##########################" | tee -a $LogFile
        echo  "$logline Dateihandling nachdem FILEBOT fertig ist" | tee -a $LogFile
        echo  "$logline Datei wurde nach ~${1%/*.mkv} verschoben" | tee -a $LogFile

        ## Ermittle Dateigröße
        DUCMD="$(which \du) -m"
        FileSize1=$($DUCMD "$1" | cut -f1)
        cd /
fi

## Neues Erstelldatum, dass XBMC es unter "recently added" führt
echo "$logline Neues Erstelldatum" | tee -a $LogFile
touch -c "$1"

## Vergebe der Datei alle Rechte
echo "$logline CHMOD 777" | tee -a $LogFile
chmod 777 "$1"
Final=$($DUCMD "$1" | cut -f1)
Final2=$(echo "$Final" | sed -e :a -e 's/\(.*[0-9]\)\([0-9]\{3\}\)/\1.\2/;ta')

## Lösche leere Ordner       
echo "$logline Lösche leere Ordner" | tee -a $LogFile
cd /root/.pyload/Downloads
find . -type d -empty -exec rmdir {} \;

## Sende Push (aber nur MKV)
if grep -q ".mkv" "$1"; then
        echo "$logline PUSH senden" | tee -a $LogFile
        API="YOURKEY"
        curl -u $API: https://api.pushbullet.com/v2/pushes -d type=note -d title="INFO: $mailtitle runtergeladen" -d body="Verschoben nach:%09 ~/NAS_HD$pfad/%0d%0dGroesse:%09$Final2 MB"
        #echo -e "Verschoben nach:\t ~/NAS_HD$pfad/\n\nGroesse:\t$Final2 MB\n\n\nSincerly\nyour lovely NAS" | mailx -s "INFO: $mailtitle runtergeladen" hfdgdg7@gmail.com;
fi

## Sende Dateien an NAS (wenn er online ist)
if ping -c4 192.168.0.107 2>&1 >/dev/null; then
        mount -a
        echo "$logline NAS ist online - verschiebe Datei dorthin" | tee -a $LogFile
        rsync --remove-source-files -rvhP "$1" "/mnt/HD/NAS_Medien$pfad/"  --exclude Music
else
        echo "$logline NAS ist offline - verschiebe keine Daten" | tee -a $LogFile
fi
