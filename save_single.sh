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
img_pathname=$1
img_basename=${img_pathname##*/}
img_noext=${img_basename%.*}

if [[ ${dest_dir:0:1} != '/' ]]; then
  dest_dir=$(tr '[:upper:]' '[:lower:]' <<<"$HOME/$dest_dir")
fi

if [[ ${save_to_current} == true ]]; then
  if fwin=$(osascript -e 'tell application "Finder" to get POSIX path of (insertion location as alias)' 2>/dev/null); then
    dest_dir=$fwin
  fi
fi

if [[ -r $img_pathname ]]; then
  # make sure dest_dir exists
  if [[ ! -d $dest_dir ]]; then
    /bin/mkdir -p "$dest_dir" || break_err 1 "failed to create output dir"
  fi
  fmt=${format:-png}
  destfile=$dest_dir/${img_noext}.$fmt
  if [[ ${img_pathname} == "${destfile}" ]]; then
    break_err 1 "(source and destination filename were the same)"
  fi
  if /usr/bin/sips -s format $fmt "$img_pathname" --out "$dest_dir/${img_noext}.$fmt"; then
    if [[ ${delete_after_convert} == true ]] && [[ -n $dataHash ]]; then
      /usr/bin/sqlite3 "$db_path/$db_name" "DELETE FROM clipboard WHERE dataHash = \"$dataHash\" AND dataType = 1 LIMIT 1;"
      rm "$img_pathname"
    fi
    open -a Finder "$dest_dir"
    break_err 0
  else
    break_err 1
  fi
else
  break_err 1
fi
