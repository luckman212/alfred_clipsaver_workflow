#!/bin/zsh --no-rcs

# URI scheme: https://cleanshot.com/docs-api

# ensure deps
if ! hash pngpaste &>/dev/null; then brew install --quiet pngpaste; fi

# workaround for CleanShot bug
# open-annotate verb does not work for TIFFs (bugreport has been filed!)
_convert_to_png() {
  temp_dir=${temp_dir:-/private/tmp/converted_images}
  if [[ ! -d ${temp_dir} ]]; then
    mkdir -p "${temp_dir}"
  else
    find "${temp_dir}" -type f -ctime +10m -delete 2>/dev/null
  fi
  for img_pathname in "$@"; do
    [[ -r ${img_pathname} ]] || continue
    [[ ${(L)img_pathname} == *.png ]] && continue
    img_basename=${img_pathname##*/}
    img_noext="${img_basename%.*}"
    out_fname="$temp_dir/${img_noext}.png"
    if /usr/bin/sips 2>&1 \
      --setProperty format png \
      --out "${out_fname}" \
      "${img_pathname}"; then
      EXCLUDE+=( "$img_pathname" )
      FILEARRAY+=( "$out_fname" )
    fi
  done
}

_process() {
  echo 1>&2 "processing: $1"
  open "cleanshot://${VERB}?filepath=$1"
}

if [[ -z $alfred_workflow_uid ]]; then
  echo "this script is meant to be used from within an Alfred workflow"
  exit
fi

#normalize input
IFS=$'\t' read -A FILEARRAY <<<"$1"
shift
for a in $@ ; do
  FILEARRAY+=( $a )
done

action=${action:-edit}
#echo 1>&2 "action: $action"
EXCLUDE=()

case "$action" in
  clipboard)
    imgfile='/private/tmp/clipboard.png'
    VERB='open-annotate'
    if /opt/homebrew/bin/pngpaste 2>/dev/null $imgfile ; then
      _process $imgfile
    else
      /usr/bin/afplay /System/Library/Sounds/Bottle.aiff
    fi
    exit
    ;;
  float|pin)
    VERB='pin'
    ;;
  edit|annotate)
    VERB='open-annotate'
    _convert_to_png "${FILEARRAY[@]}"
    ;;
esac

#about the zsh ${FOO:|BAR} syntax (array subtraction expression)
#returns elements of $FILEARRAY that are not present in $EXCLUDE
#https://zsh.sourceforge.io/Doc/Release/Expansion.html#Parameter-Expansion
#https://chatgpt.com/c/177a7413-03a8-47a0-a3d4-92660eee188a
for f in ${FILEARRAY:|EXCLUDE}; do
  _process "$f"  
done
