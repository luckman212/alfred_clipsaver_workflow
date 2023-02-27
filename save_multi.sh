#!/usr/bin/env bash

function break_err() {
cat <<EOF
{ "alfredworkflow": {
    "arg": "",
    "variables": {
      "exitcode": $1,
      "errmsg": "$2"
    }
  }
}
EOF
exit
}

unset errmsg
num_items=$1
max_clips=$(/usr/bin/sqlite3 "$db_path/$db_name" "SELECT COUNT(dataHash) FROM clipboard WHERE dataType = 1;")

re='^[0-9]+$'
if ! [[ $num_items =~ $re ]] ; then
  break_err 2 "not a number (NaN)"
fi

if [[ $num_items -eq 0 ]] ; then
  break_err 2 "num_items must be >0"
fi

if [[ $max_clips -eq 0 ]]; then
  break_err 2 "no image clips found in the database"
fi

if [[ $max_clips -lt "$num_items" ]]; then
  errmsg="not enough clips to fulfill request\nrequested: $num_items, available: $max_clips (adjusted)"
  num_items=$max_clips
fi

# fetch image clips from database
clip_list=$(/usr/bin/sqlite3 "$db_path/$db_name" "SELECT dataHash from clipboard WHERE dataType = 1 ORDER BY rowid DESC LIMIT $num_items;")

if [[ $save_to_current == "true" ]]; then
  if fwin=$(osascript -e 'tell application "Finder" to get POSIX path of (insertion location as alias)' 2>/dev/null); then
    dest_dir=$fwin
  fi
fi

if [[ ${dest_dir:0:1} != '/' ]]; then
  dest_dir=$(tr '[:upper:]' '[:lower:]' <<<"$HOME/$dest_dir")
fi

# make sure dest_dir exists
if [[ ! -d $dest_dir ]]; then
  if ! /bin/mkdir -p "$dest_dir"; then
    break_err 2 "failed to create dest_dir:\n$dest_dir"
  fi
fi

fmt=${format:-png}

# loop and process
for src_fname in $clip_list; do

  tiff_name=$db_path/${db_name}.data/$src_fname
  src_basename=${src_fname%.tiff}

  if [[ -r $tiff_name ]]; then
    if /usr/bin/sips -s format $fmt "$tiff_name" --out "$dest_dir/${src_basename}.$fmt" &>/dev/null; then
      if [[ ${delete_after_convert} == true ]]; then
        /usr/bin/sqlite3 "$db_path/$db_name" "DELETE FROM clipboard WHERE dataHash = \"$src_fname\" AND dataType = 1 LIMIT 1;"
        rm "$tiff_name" &>/dev/null
      fi
    else
      errmsg="failed: $src_basename\n$errmsg"
    fi
  else
    errmsg="not found: $src_basename\n$errmsg"
  fi

done

# if ALL images were processed, run cleanup script
if [[ $num_items -eq $max_clips ]]; then
  ./alfred_validate_cache.sh
fi

if [[ -n $errmsg ]]; then
  break_err 1 "$errmsg"
fi

break_err 0
