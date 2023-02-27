#!/usr/bin/env bash

# cleans up orphan image files that no longer exist in Alfred's db

if [[ -z $db_path ]]; then
  db_path='Library/Application Support/Alfred/Databases/'
fi

if [[ -z $db_name ]]; then
  db_name='clipboard.alfdb'
fi

orphan_dir=$HOME/Desktop/orphan_images

function open_orphan_dir() {
  if [[ -d $orphan_dir ]]; then
    open -a Finder "$orphan_dir"
  fi
}

case $1 in
  -o|--open) #open dirs
    open -a Finder "$db_path/$db_name.data"
    open_orphan_dir
    exit
    ;;
esac

# populate array with list of image clips from database
clipArray=()
while IFS= read -r line; do clipArray+=("$line"); done < <(/usr/bin/sqlite3 "$db_path/$db_name" "SELECT dataHash FROM clipboard WHERE dataType = 1;")

# loop thru all tiffs in database storage folder, and validate
cd "$db_path/$db_name.data" || { echo "could not cd to db storage folder"; exit 1; }

shopt -s nullglob  # enable
for i in *.tiff *.png ; do
  if [[ ! " ${clipArray[@]} " =~ " ${i} " ]]; then
    echo "orphan: $i"
    if [[ ! -d $orphan_dir ]]; then
      if ! mkdir -p "$orphan_dir"; then
        echo "failed to create $orphan_dir"
        exit 1
      fi
    fi
    mv "$i" "$orphan_dir/"
  fi
done
shopt -u nullglob  # disable

open_orphan_dir
