#!/usr/bin/env bash

function break_err() {
cat <<EOF
{ "alfredworkflow": {
    "arg": "",
    "variables": {
      "exitcode": $1
    }
  }
}
EOF
exit
}

tiff_pathname="$1"
tiff_basename=${tiff_pathname##*/}
tiff_noext="${tiff_basename%.tiff}"

cd
if [[ $save_to_current == "true" ]]; then
  if fwin=$(osascript -e 'tell application "Finder" to get POSIX path of (insertion location as alias)' 2>/dev/null); then
    dest_dir="$fwin"
  fi
fi

if [[ -r $tiff_pathname ]]; then

  # make sure dest_dir exists
  if [[ ! -d $dest_dir ]]; then
    /bin/mkdir -p "$dest_dir" || break_err 1
  fi
  fmt=${format:-png}
  if /usr/bin/sips -s format $fmt "$tiff_pathname" --out "$dest_dir/${tiff_noext}.$fmt"; then
    /usr/bin/sqlite3 "$HOME/$db_path/$db_name" "DELETE FROM clipboard WHERE dataHash = \"$tiff_basename\" AND dataType = 1 LIMIT 1;"
    rm "$tiff_pathname"
    open -a Finder "$dest_dir"
    break_err 0
  else
    break_err 1
  fi

else

  break_err 1

fi
