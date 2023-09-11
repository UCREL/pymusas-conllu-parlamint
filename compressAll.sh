#!/bin/bash

# Update to match your storage pool location
STORAGE="/mnt/zfs/ucrel-data"

# Grab every directory in the storage pool
PATH_LIST=$(ls -d $STORAGE/*/)

# For each directory, compress into a .tar.gz matching the same name
for path in $PATH_LIST; do
	input=${path%/}
	output=$input.tar.gz

	# Note; tar set to skip input.conllu and output.conllu left over from processing
	tar -cvzf $output -C $path --exclude={input.conllu,output.conllu} $input
done
