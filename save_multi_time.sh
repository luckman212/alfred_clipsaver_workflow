#!/usr/bin/env bash

exec 3>&1

function break_err() {
exec 1>&3
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

exec 1>/dev/null

unset errmsg
atleast=$1

re='^[0-9]+$'
if ! [[ $atleast =~ $re ]] ; then
  break_err 2 "not a number (NaN)"
fi

if [[ $atleast -eq 0 ]] ; then
  break_err 2 "atleast must be >0"
fi

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

# fetch image clips from database, loop and process
while read -r src_fname ; do
  #echo 1>&2 "processing: [$src_fname]"
  source ./process_clip.bash
done < <(./get_image_hashes.py --atleast "$atleast")

if [[ -n $errmsg ]]; then
  break_err 1 "$errmsg"
fi

break_err 0
