#!/bin/bash

# wrapper script to run pymusas_conllu docker container on multiple years of ParlaMint CoNLL-U format files (to depth 1)

# run this script in the unzipped folder containing the years as subdirectories

# ignore exit codes so this keeps running
set +e

# Grab the total core count for this host
THREADS=$(grep -c ^processor /proc/cpuinfo)

# Pick a specific folder by passing it as an argument
FOLDER="$1"

# loop through all the years, in parallel up to THREADS times
ls "$FOLDER" | xargs -I {} -n 1 -P $THREADS /opt/pymusas-conllu-parlamint-main/pymusas_job.sh $FOLDER {}
