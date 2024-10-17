#!/bin/bash

# Don't push this too high else you'll completely saturate your downlink
THREADS=10

# Update to match the storage pool you're using
STORAGE="/mnt/pool/ucrel-data"

# Grab the URL list via lynx so we can iterate over it
URL_LIST=$(lynx --dump --listonly --nonumbers --display_charset=utf-8 https://nl.ijs.si/et/tmp/ParlaMint/MT/CoNLL-U-en/ | grep .zip)

# Limited parallel threads to download each one
echo $URL_LIST | xargs -n 1 -P $THREADS wget -nv -c -P "$STORAGE"

# List and extract (in parallel) each of the downloaded .zip's
ZIP_LIST=$(ls $STORAGE/*.zip)
echo $ZIP_LIST | xargs -n 1 -P $THREADS unzip -d "$STORAGE"
