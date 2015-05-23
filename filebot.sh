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
API="nxxxxxx"

## Schreib was in den pyLoad Log
echo  "$logline ##########################" | tee -a $LogFile
echo  "$logline Dateihandling nachdem FILEBOT fertig ist" | tee -a $LogFile

if [[ $1 == *".mkv" ]] || [[ $1 == *".avi" ]] || [[ $1 == *".mp4" ]]; then
  echo  "$logline Datei wurde nach ~$pfad_00 verschoben" | tee -a $LogFile
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
if [[ $1 == *".mkv" ]] || [[ $1 == *".avi" ]] || [[ $1 == *".mp4" ]]; then
  Final=$($DUCMD "$1" | cut -f1)
  Final2=$(echo "$Final" | sed -e :a -e 's/\(.*[0-9]\)\([0-9]\{3\}\)/\1.\2/;ta')
fi

## Lösche leere Ordner
echo "$logline Lösche leere Ordner" | tee -a $LogFile
cd /root/.pyload/Downloads
find . -type d -empty -exec rmdir {} \;

## Sende Push (aber nur Filmdateien)
function push {
  echo "$logline PUSH senden" | tee -a $LogFile
  if [[ $2 == "online" ]]; then
    curl -u $API: https://api.pushbullet.com/v2/pushes -d type=note -d title="pyLoad: FileBot sorted '$mailtitle'" -d body="Server is online!%0Amoved File to: /NAS_Medien$pfad/%0A%0AFilesize: $Final2 MB" 2>&1 >/dev/null
  else
    curl -u $API: https://api.pushbullet.com/v2/pushes -d type=note -d title="pyLoad: FileBot sorted '$mailtitle'" -d body="moved File to: /mnt/HD/Medien$pfad/%0A%0AFilesize: $Final2 MB" 2>&1 >/dev/null
  fi
}

if [[ $1 == *".mkv" ]] || [[ $1 == *".avi" ]] || [[ $1 == *".mp4" ]]; then
## Sende Dateien an NAS (wenn er online ist)
  if ping -c4 192.168.0.107 2>&1 >/dev/null; then
    mount -a
    echo "$logline NAS ist online - verschiebe Datei dorthin" | tee -a $LogFile
    push "$1" "online"
    rsync --remove-source-files -rvh "$1" "/mnt/HD/NAS_Medien$pfad/" --exclude='Music' --exclude='TVHeadend' --exclude='Anime' | grep -E '*mkv|*avi|*mp4'
  else
    echo "$logline NAS ist offline - verschiebe keine Daten" | tee -a $LogFile
    push "$1" "offline"
  fi
else
  echo "$logline $mailtitle_ext ist kein Film"
fi
