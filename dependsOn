#!/usr/bin/env bash

# the new hotness
jq -r "select(IN(.dependencies[]; \"$1\" )) | input_filename" -- "${@:2}"

# old and busted
rg "^\s+\"${1}\",?" --files-with-matches | sort

