#!/bin/bash

# Need to download cwebp and put /bin/.exe into this directory https://developers.google.com/speed/webp/download 
# Need to run in the same directory as avatars

PARAMS=('-m 6 -q 70 -mt -af -progress -resize 180 180')
basepwd=$PWD

if [ $# -ne 0 ]; then
	PARAMS=$@;
fi

shopt -s nullglob nocaseglob extglob

cd "$basepwd/assets/dyn/arts/charavatars/"

for FILE in *.@(jpg|jpeg|tif|tiff|png); do 
    $basepwd/convert/cwebp.exe $PARAMS "$FILE" -o "${FILE%.*}".webp;
done

cd "./elite"

for FILE in *.@(jpg|jpeg|tif|tiff|png); do 
    $basepwd/convert/cwebp.exe $PARAMS "$FILE" -o "${FILE%.*}".webp;
done
