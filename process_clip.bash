#shellcheck shell=bash

# this is meant to be sourced from save_multi{_time}.sh

if [[ $src_fname == */* ]]; then
  # from plist
  src_basename=${src_fname##*/}
  src_basename_noext=${src_basename%.*}
  if [[ -r $src_fname ]]; then
    if ! /usr/bin/sips -s format $fmt "$src_fname" --out "$dest_dir/${src_basename_noext}.$fmt" &>/dev/null; then
      errmsg="failed: $src_basename\n$errmsg"
    fi
  else
    errmsg="not found: $src_basename\n$errmsg"
  fi
else
  # from Alfred db
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
fi
