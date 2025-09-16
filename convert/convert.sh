#!/bin/bash

# Need to download cwebp and put /bin/.exe into this directory https://developers.google.com/speed/webp/download 
# Need to run in the same directory as avatars

PARAMS=('-q 25 -alpha_q 25 -m 6 -af -mt -progress -resize 180 180')
basepwd=$PWD

if [ $# -ne 0 ]; then
	PARAMS=$@;
fi

shopt -s nullglob nocaseglob extglob

cd "$basepwd/assets/dyn/arts/charavatars/"

for FILE in *.@(jpg|jpeg|tif|tiff|png); do 
    cwebp $PARAMS "$FILE" -o "${FILE%.*}".webp;
done

cd "./elite"

for FILE in *.@(jpg|jpeg|tif|tiff|png); do 
    cwebp $PARAMS "$FILE" -o "${FILE%.*}".webp;
done
