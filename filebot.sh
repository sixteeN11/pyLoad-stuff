#!/bin/bash
## String Manipulation
mailtitle_ext=${1##*/}
mailtitle=${mailtitle_ext%.*}
pfad_00=${1%/*.mkv}
pfad=${pfad_00##*/Medien}

##Pushbullet API
API="n6n3Zb1wkwWhyTist1uX7GiAUdmLk8Ou"

## Schreib was in den pyLoad Log
echo  "ExternaScript:  ##########################"
echo  "ExternaScript:  Dateihandling nachdem FILEBOT fertig ist"

if [[ $1 == *".mkv" ]] || [[ $1 == *".avi" ]] || [[ $1 == *".mp4" ]]; then
  echo  "ExternaScript:  Datei wurde nach ~$pfad_00 verschoben"
  ## Ermittle Dateigroeße
  DUCMD="$(which \du) -m"
  FileSize1=$($DUCMD "$1" | cut -f1)
  cd /
fi

## Neues Erstelldatum, dass XBMC es unter "recently added" fuehrt
echo "ExternaScript:  Neues Erstelldatum"
touch -c "$1"

## Vergebe der Datei alle Rechte
echo "ExternaScript:  CHMOD 777"
chmod 777 "$1"
if [[ $1 == *".mkv" ]] || [[ $1 == *".avi" ]] || [[ $1 == *".mp4" ]]; then
  Final=$($DUCMD "$1" | cut -f1)
  Final2=$(echo "$Final" | sed -e :a -e 's/\(.*[0-9]\)\([0-9]\{3\}\)/\1.\2/;ta')
fi

## Loesche leere Ordner
echo "ExternaScript:  Loesche leere Ordner"
cd /root/.pyload/Downloads
find . -type d -empty -exec rmdir {} \;

## Sende Push (aber nur Filmdateien)
function push {
  echo "ExternaScript:  PUSH senden"
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
    echo "ExternaScript:  NAS ist online - verschiebe Datei dorthin"
    push "$1" "online"
    rsync --remove-source-files -rvh "$1" "/mnt/HD/NAS_Medien$pfad/" --exclude='Music' --exclude='TVHeadend' --exclude='Anime' | grep -E '*mkv|*avi|*mp4' 2>&1 >/dev/null
  else
    echo "ExternaScript:  NAS ist offline - verschiebe keine Daten"
    push "$1" "offline"
  fi
else
  echo "ExternaScript:  $mailtitle_ext ist kein Film"
fi
