#!/bin/zsh --no-rcs

# workaround for CleanShot bug
# open-annotate verb does not work for TIFFs
# bugreport has been filed!
_convert_to_png() {
  temp_dir=${temp_dir:-/private/tmp/converted_images}
  if [[ ! -d ${temp_dir} ]]; then
    mkdir -p "${temp_dir}"
  else
    find "${temp_dir}" -type f -ctime +10m -delete 2>/dev/null
  fi
  for img_pathname in "$@"; do
    [[ -r ${img_pathname} ]] || continue
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

action=${action:-edit}
#echo 1>&2 "action: $action"
IFS=$'\t' read -A FILEARRAY <<<"$1"
EXCLUDE=()

case "$action" in
  float|pin)
    VERB='pin'
    ;;
  edit|annotate)
    VERB='open-annotate'
    _convert_to_png "${FILEARRAY[@]}"
    ;;
esac

for f in ${FILEARRAY:|EXCLUDE}; do
  echo 1>&2 "processing: $f"
  open "cleanshot://${VERB}?filepath=$f"
done
