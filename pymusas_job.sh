#!/bin/bash

set +e

# Grab a parent folder and target year from the arg list
FOLDER="$1"
year="$2"

# Set our CWD to the parent folder
cd $FOLDER

echo "`date`: Processing year $year" >> $FOLDER/pymusas_conllu.$year.log 2>&1
cd $year >> $FOLDER/pymusas_conllu.$year.log 2>&1
# loop through all the files within one year
for file in *.conllu
do
    # set up file with appropriate input name
    cp $file input.conllu >> $FOLDER/pymusas_conllu.$year.log 2>&1
    # run pymusas inside docker
    docker run -v "$FOLDER/$year:/mnt/host:rw" --rm pymusas_conllu >> $FOLDER/pymusas_conllu.$year.log 2>&1
    # to do: add some simple sanity checks e.g. input and output line count should be equal
    # rename output file back to original filename
    rm $file >> $FOLDER/pymusas_conllu.$year.log 2>&1
    # mv output.conllu `basename $file .conllu`-pymusas.conllu
    mv output.conllu $file >> $FOLDER/pymusas_conllu.$year.log 2>&1
    # write log
    echo "`date`: Tagged file $file" >> $FOLDER/pymusas_conllu.$year.log 2>&1
    # Also echo the log here so we see it in the parent process (otherwise we don't get any progress indication!)
    echo "`date`: Tagged file $file"
done
# tidy up temporary file
rm input.conllu >> $FOLDER/pymusas_conllu.$year.log 2>&1
# go back to parent folder to progress to next year
cd $FOLDER >> $FOLDER/pymusas_conllu.$year.log 2>&1
